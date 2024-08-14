"""
OAuth2 with Password (and hashing), Bearer with JWT tokens:
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#oauth2-with-password-and-hashing-bearer-with-jwt-tokens
OAuth2 scopes:
https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/#oauth2-scopes
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
import util
from .schemas import AuthUser

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

fake_users_db = [
    # password admin
    {"id": 1,
     "username": "admin",
     "email": "vl@key-info.com.ua",
     "phone": "+380504434316",
     "first_name": "Volodymyr",
     "last_name": "Letiahin",
     'role': ["admin"],
     "disabled": False,
     "login_denied": False,
     "hashed_password": "$2a$10$Dlw.zzMjzvLiklyECarLHusaPyY/Mz75fSQAB4z.f1pSk/Vfp.Uxu"
     },
    # password client
    {"id": 2,
     "username": "manager",
     "email": "vl@key-info.com.ua",
     "phone": "+380504434316",
     "first_name": "Volodymyr",
     "last_name": "Letiahin",
     "role": ["items:read", "items:write", "users:read", "users:write"],
     "disabled": False,
     "login_denied": False,
     'hashed_password': '$2a$10$YSpfBRAvvtRBzO8FCC0vLuWm3vBIJPcn9Ah7etEKVBJ7Zf7ISyIeu',
     }
]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


# class User(BaseModel):
#     id: int
#     username: str
#     email: str | None = None
#     phone: str | None = None
#     first_name: str | None = None
#     last_name: str | None = None
#     role: list[str] = []
#     disabled: bool | None = None
#     login_denied: bool | None = None


class UserInDB(AuthUser):
    hashed_password: str


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


def get_user(db, username: str):
    for user_record in db:
        if username in user_record["username"]:
            user_dict = user_record
            return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)

    if not user:  # Check if User exist
        return False

    if user.login_denied:  # Check if User login allowed
        return False

    if not verify_password(password, user.hashed_password):  # heck if User password is valid
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# User has valid token
async def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(OAUTH2_SCHEME)]):

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
        token_data = TokenData(scopes=token_scopes, username=username)

    except (InvalidTokenError, ValidationError) as token_error:
        if str(token_error) == "Signature has expired":
            credentials_exception.detail = "Token has expired"
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            credentials_exception.detail = "Not enough permissions"
            raise credentials_exception

    return user


# User has valid token and NOT disabled
async def get_current_active_user(current_user: Annotated[AuthUser, Security(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="User disabled")
    return current_user


class RBAC:  # Role-based access control (RBAC) system where access permission (ACL) based on User's role.
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
