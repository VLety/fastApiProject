"""
RESTful OpenAPI Specification (OAS) application programming interface (API) based on FastAPI framework
Documentation: api-url/docs
"""
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from sqlalchemy.sql.functions import current_user

import util
from sql_app import crud, models, schemas, auth
from sql_app.database import SessionLocal, engine

APP_CONFIG = util.get_config()
models.Base.metadata.create_all(bind=engine)

# Behind a Proxy root_path argument
# https://fastapi.tiangolo.com/advanced/behind-a-proxy/#behind-a-proxy
# Metadata and Docs URLs
# https://fastapi.tiangolo.com/tutorial/metadata/#metadata-and-docs-urls
app = FastAPI(root_path=APP_CONFIG["root_path"],
              title=APP_CONFIG["api_docs"]["title"],
              version=APP_CONFIG["api_docs"]["version"],
              summary=APP_CONFIG["api_docs"]["summary"],
              description=APP_CONFIG["api_docs"]["description"],
              terms_of_service=APP_CONFIG["api_docs"]["terms_of_service"],
              contact=APP_CONFIG["api_docs"]["contact"],
              license_info=APP_CONFIG["api_docs"]["license_info"],
              openapi_tags=APP_CONFIG["api_docs"]["openapi_tags"])

# CORS (Cross-Origin Resource Sharing)
# https://fastapi.tiangolo.com/tutorial/cors/#cors-cross-origin-resource-sharing
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=APP_CONFIG["cors"]["allow_origins"],
    allow_credentials=APP_CONFIG["cors"]["allow_credentials"],
    allow_methods=APP_CONFIG["cors"]["allow_methods"],
    allow_headers=APP_CONFIG["cors"]["allow_headers"]
)


# Dependency -> We need to have an independent database session/connection (SessionLocal) per request, use the same
# session through all the request and then close it after the request is finished. And then a new session will be
# created for the next request.
#
# Also, we can add "Alternative DB session" with middleware function (with relevant + and -)
# A "middleware" is basically a function that is always executed for each request,
# with some code executed before, and some code executed after the endpoint function.
# https://fastapi.tiangolo.com/tutorial/sql-databases/#alternative-db-session-with-middleware
# @app.middleware("http")
# async def db_session_middleware(request: Request, call_next):
#     response = Response("Internal server error", status_code=500)
#     try:
#         request.state.db = SessionLocal()
#         response = await call_next(request)
#     finally:
#         request.state.db.close()
#     return response
#
# # Dependency
# def get_db(request: Request):
#     return request.state.db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/favicon.ico', include_in_schema=False)  # Exclude request from DOCS schema
async def favicon():
    # https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse
    return FileResponse("./static/favicon.ico")


# Create (POST)
@app.post("/users/", response_model=schemas.User, tags=["Users"])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if unique User's identification attributes already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered!")
    db_user = crud.get_user_by_email(db, email=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered!")

    return crud.create_user(db=db, user=user)


# Read (GET)
@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
async def read_user(
        user_id: int,
        db: Session = Depends(get_db),
        authorize: bool = Depends(auth.RBAC(acl=["admin", "users:read"]))
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found!")
    return db_user


# Update (PUT)
@app.put("/users/{user_id}", response_model=schemas.User, tags=["Users"])
async def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if User exists
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found!")

    return crud.update_user(db=db, db_user=db_user, user=user)


# Delete (DELETE)
@app.delete("/users/{user_id}", tags=["Users"])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Check if User exists
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found!")

    return crud.delete_user(db=db, db_user=db_user)


@app.get("/users/", response_model=list[schemas.User], tags=["Users"])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users/{user_id}/items/", response_model=schemas.Item, tags=["Items"])
async def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item], tags=["Items"])
async def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: auth.Annotated[auth.OAuth2PasswordRequestForm, Depends()], ) -> auth.Token:
    user = auth.authenticate_user(auth.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return auth.Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=auth.AuthUser, tags=["Authentication"])
async def read_users_me(
        current_user: auth.Annotated[auth.AuthUser, Depends(auth.get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/", tags=["Authentication"])
async def read_own_items(
        current_user: auth.Annotated[auth.AuthUser, auth.Security(auth.get_current_active_user, scopes=["items"])]
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/status/", tags=["Authentication"])
async def read_system_status(current_user: auth.Annotated[auth.AuthUser, Depends(auth.get_current_user)]):
    return {"status": "ok"}

# @app.post("/token", tags=["Authentication"])
# async def login_for_access_token(form_data: auth.Annotated[auth.OAuth2PasswordRequestForm, Depends()], ) -> auth.Token:
#     user = auth.authenticate_user(auth.fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=auth.status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = auth.create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return auth.Token(access_token=access_token, token_type="bearer")
#
#
# @app.get("/users/me/", response_model=auth.AuthUser, tags=["Authentication"])
# async def read_users_me(current_user: auth.Annotated[auth.AuthUser, Depends(auth.get_current_active_user)], ):
#     return current_user
#
#
# @app.get("/users/me/items/", tags=["Authentication"])
# async def read_own_items(current_user: auth.Annotated[auth.AuthUser, Depends(auth.get_current_active_user)], ):
#     return [{"item_id": "Foo", "owner": current_user.username}]
