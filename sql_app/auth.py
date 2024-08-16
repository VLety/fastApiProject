"""
OAuth2 with Password (and hashing), Bearer with JWT tokens:
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#oauth2-with-password-and-hashing-bearer-with-jwt-tokens
OAuth2 scopes:
https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/#oauth2-scopes
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated
from pydantic import ValidationError
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import util
from .schemas import AuthUser, AuthTokenData
from . import crud
from .database import get_db

APP_CONFIG = util.get_config()
SECRET_KEY = APP_CONFIG["auth"]["SECRET_KEY"]  # to get a SECRET_KEY run in terminal: openssl rand -hex 32
ALGORITHM = APP_CONFIG["auth"]["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = APP_CONFIG["auth"]["ACCESS_TOKEN_EXPIRE_MINUTES"]
PWD_CONTEXT = CryptContext(schemes=APP_CONFIG["auth"]["PWD_CONTEXT"]["schemes"],
                           deprecated=APP_CONFIG["auth"]["PWD_CONTEXT"]["deprecated"])
OAUTH2_SCHEME = OAuth2PasswordBearer(
    tokenUrl=APP_CONFIG["auth"]["OAUTH2_SCHEME"]["tokenUrl"],
    scopes=APP_CONFIG["auth"]["OAUTH2_SCHEME"]["scopes"]
)

"""
{
  "username": "manager",
  "first_name": "Volodymyr",
  "last_name": "Letiahin",
  "phone": "+380504434317",
  "email": "vlety@key-info.com.ua",
  "role": [
    "manager"
  ],
  "disabled": false,
  "login_denied": false,
  "password": "manager"
}
"""


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


def authenticate_user(db_user, password: str):

    if not db_user:  # Check if User exist
        return False

    if db_user.login_denied:  # Check if User login allowed
        return False

    if not verify_password(password, db_user.hashed_password):  # heck if User password is valid
        return False

    return db_user


def create_access_token(data: dict, expires_delta: timedelta):  # timedelta | None = None
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    # if expires_delta:
    #     expire = datetime.now(timezone.utc) + expires_delta
    # else:
    #     expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# User has valid token
async def get_current_user(security_scopes: SecurityScopes,
                           token: Annotated[str, Depends(OAUTH2_SCHEME)],
                           db: Session = Depends(get_db)):

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        # payload: {'sub': 'admin', 'scopes': [], 'exp': 1723557087}
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_scopes = payload.get("scopes", [])
        token_data = AuthTokenData(scopes=token_scopes, username=username)

    except (InvalidTokenError, ValidationError) as token_error:
        if str(token_error) == "Signature has expired":
            credentials_exception.detail = "Token has expired"
        raise credentials_exception

    db_user = crud.get_user_by_username(db, username=token_data.username)

    if db_user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            credentials_exception.detail = "Not enough permissions"
            raise credentials_exception

    return db_user


# User has valid token and NOT disabled
async def get_current_active_user(current_user: Annotated[AuthUser, Security(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="User disabled")
    return current_user


# Role-based access control (RBAC) system where access permission (ACL) based on User's role.
class RBAC:
    def __init__(self, acl: list[str]) -> None:
        self.acl = acl

    def __call__(self, user: AuthUser = Depends(get_current_active_user)) -> bool:
        for permission in self.acl:
            if permission in user.role:
                return True

        # Raise UNAUTHORIZED error if permission is not exists in User's roles
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions"
        )
