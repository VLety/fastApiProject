from datetime import datetime, timedelta, timezone
from typing import Annotated
from pydantic import ValidationError
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from util import get_config, raise_http_error
from .schemas import UserResponse, AuthTokenData
from . import crud
from .database import get_db

APP_CONFIG = get_config()
SECRET_KEY = APP_CONFIG["auth"]["SECRET_KEY"]
ALGORITHM = APP_CONFIG["auth"]["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = APP_CONFIG["auth"]["ACCESS_TOKEN_EXPIRE_MINUTES"]
PWD_CONTEXT = CryptContext(schemes=APP_CONFIG["auth"]["PWD_CONTEXT"]["schemes"],
                           deprecated=APP_CONFIG["auth"]["PWD_CONTEXT"]["deprecated"])
OAUTH2_SCHEME = OAuth2PasswordBearer(
    tokenUrl=APP_CONFIG["auth"]["OAUTH2_SCHEME"]["tokenUrl"],
    scopes=APP_CONFIG["auth"]["OAUTH2_SCHEME"]["scopes"]
)


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


def authenticate_user(db_user, password: str):
    if not db_user:  # Check if User exist
        return False

    if not verify_password(password, db_user.hashed_password):  # heck if User password is valid
        return False

    if db_user.login_denied:  # Check if User login allowed
        raise_http_error(APP_CONFIG["raise_error"]["user_login_denied"])

    return db_user


def create_access_token(data: dict, expires_delta: timedelta):  # timedelta | None = None
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# User has valid token
async def get_current_user(security_scopes: SecurityScopes,
                           token: Annotated[str, Depends(OAUTH2_SCHEME)],
                           db: Session = Depends(get_db)):

    # A server using HTTP authentication will respond with a 401 Unauthorized response to a request for a protected
    # resource. This response must include at least one WWW-Authenticate header and at least one challenge,
    # to indicate what authentication schemes can be used to access the resource (and any additional data that each
    # particular scheme needs).
    if security_scopes.scopes:
        exception_headers = {"WWW-Authenticate": "Bearer scope=" + security_scopes.scope_str}
    else:
        exception_headers = {"WWW-Authenticate": "Bearer"}

    try:
        # Try to get data from Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # payload: {'sub': 'admin', 'scopes': ['scope_example'], 'exp': 1723557087}
        username: str = payload.get("sub")
        if username is None:
            raise_http_error(APP_CONFIG["raise_error"]["could_not_validate_credentials"], headers=exception_headers)
        token_scopes = payload.get("scopes", [])
        token_data = AuthTokenData(scopes=token_scopes, username=username)

        # Try to get User from database by username
        db_user = crud.get_user_by_username(db=db, username=token_data.username)
        if db_user is None:
            raise_http_error(APP_CONFIG["raise_error"]["incorrect_user_name_or_password"], headers=exception_headers)

        # Security SCOPE validation
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise_http_error(APP_CONFIG["raise_error"]["not_enough_permissions"], headers=exception_headers)

        return db_user

    except (InvalidTokenError, ValidationError) as token_error:
        if str(token_error) == "Signature has expired":  # ValidationError respond
            raise_http_error(APP_CONFIG["raise_error"]["token_has_expired"], headers=exception_headers)
        else:
            raise_http_error(APP_CONFIG["raise_error"]["could_not_validate_credentials"], headers=exception_headers)


# User has valid token and NOT disabled
async def get_current_active_user(current_user: Annotated[UserResponse, Security(get_current_user)]):
    if current_user.disabled:
        raise_http_error(APP_CONFIG["raise_error"]["user_disabled"])
    return current_user


# Role-based access control (RBAC) system where access permission (ACL) based on User's roles
class RBAC:
    def __init__(self, acl: list[str]) -> None:
        self.acl = acl

    def __call__(self, user: UserResponse = Depends(get_current_active_user)) -> bool:
        for permission in self.acl:
            if permission in user.role:
                return True

        # Raise UNAUTHORIZED error if permission is not exists in User's roles
        raise_http_error(APP_CONFIG["raise_error"]["not_enough_permissions"])
