"""
RESTful OpenAPI Specification (OAS) application programming interface (API) based on FastAPI framework
Documentation: api-url/docs
"""
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Annotated
from sqlalchemy.orm import Session
import util
from sql_app import crud, models, schemas, auth
from sql_app.database import engine, get_db

APP_CONFIG = util.get_config()  # Project config data
PERMISSIONS = util.get_permissions()  # Project access permission data
models.Base.metadata.create_all(bind=engine)  # Create all empty tables by "if not exist" condition

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


@app.get('/favicon.ico', include_in_schema=False)  # Exclude request from DOCS schema
async def favicon():
    # https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse
    return FileResponse("./static/favicon.ico")


""" EMPLOYEE CRUD requests --------------------------------------------------------------------------------------- """

# Create (POST)
@app.post("/employee/", response_model=schemas.EmployeeResponse, tags=["Employee"])
async def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db),
                          permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["POST_employee"]))):
    # Check if unique employee's identification attributes already exists
    db_employee = crud.get_employee_by_email(db, email=employee.email)
    if db_employee:
        raise HTTPException(status_code=400, detail=APP_CONFIG["raise_error"]["email_already_registered"])

    db_employee = crud.get_employee_by_phone(db, phone=employee.phone)
    if db_employee:
        raise HTTPException(status_code=400, detail=APP_CONFIG["raise_error"]["phone_already_registered"])

    return crud.create_employee(db=db, employee=employee)


# Read (GET) ALL
@app.get("/employee/", response_model=list[schemas.EmployeeResponse], tags=["Employee"])
async def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                         permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["GET_employee"]))):
    return crud.get_employees(db, skip=skip, limit=limit)


# Read (GET) FIRST
@app.get("/employee/{employee_id}", response_model=schemas.EmployeeResponse, tags=["Employee"])
async def read_employee(employee_id: int, db: Session = Depends(get_db),
                        permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["GET_employee_employee_id"]))):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail=APP_CONFIG["raise_error"]["employee_not_found"])
    return db_employee


# Update (PUT) FIRST
@app.put("/employee/{employee_id}", response_model=schemas.EmployeeResponse, tags=["Employee"])
async def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db),
                          permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["PUT_employee_employee_id"]))):
    return crud.update_employee(db=db, employee_id=employee_id, employee=employee)


# Delete (DELETE) FIRST
@app.delete("/employee/{employee_id}", tags=["Employee"])
async def delete_employee(employee_id: int, db: Session = Depends(get_db),
                          permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["DELETE_employee_employee_id"]))):
    return crud.delete_employee(db=db, employee_id=employee_id)


""" USER CRUD requests --------------------------------------------------------------------------------------- """

# Create (POST)
@app.post("/user/", response_model=schemas.UserResponse, tags=["User"])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),
                      permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["POST_user"]))):
    crud.check_new_user(db, user)  # Check if new user attributes is valid
    hashed_password = auth.get_password_hash(user.password)  # Create hashed password based on PWD_CONTEXT
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)


# Read (GET) ALL
@app.get("/user/", response_model=list[schemas.UserResponse], tags=["User"])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["GET_user"]))):
    return crud.get_users(db, skip=skip, limit=limit)


# Read (GET) FIRST
@app.get("/user/{user_id}", response_model=schemas.UserResponse, tags=["User"])
async def read_user(user_id: int, db: Session = Depends(get_db),
                    permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["GET_user_user_id"]))):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=APP_CONFIG["raise_error"]["user_not_found"])
    return db_user


# Update (PUT) FIRST
@app.put("/user/{user_id}", response_model=schemas.UserResponse, tags=["User"])
async def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db),
                      permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["PUT_user_user_id"]))):
    return crud.update_user(db=db, user_id=user_id, user=user)


# Update (PUT) FIRST
@app.put("/user/{user_id}/role", response_model=schemas.UserResponse, tags=["User"])
async def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db),
                      permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["PUT_user_user_id"]))):
    return crud.update_user(db=db, user_id=user_id, user=user)


# Delete (DELETE) FIRST
@app.delete("/user/{user_id}", tags=["User"])
async def delete_user(user_id: int, db: Session = Depends(get_db),
                      permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["DELETE_user_user_id"]))):
    return crud.delete_user(db=db, user_id=user_id)


""" Authentication ------------------------------------------------------------------------------------------- """

# OAuth2PasswordRequestForm:
# This is a dependency class to collect the `username` and `password` as form data for an OAuth2 password flow.
# The OAuth2 specification dictates that for a password flow the data should be collected using form data
# (instead of JSON) and that it should have the specific fields `username` and `password`.
@app.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: auth.Annotated[auth.OAuth2PasswordRequestForm, Depends()],
                                 db: Session = Depends(get_db)
                                 ) -> schemas.AuthToken:
    db_user = crud.get_user_by_username(db, username=form_data.username)
    user = auth.authenticate_user(db_user, form_data.password)

    if not user:
        raise HTTPException(status_code=400, detail=APP_CONFIG["raise_error"]["incorrect_user_name_or_password"])

    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return schemas.AuthToken(access_token=access_token, token_type="bearer")


@app.get("/user/me/", response_model=auth.AuthUser, tags=["Authentication"])
async def read_users_me(current_user: auth.Annotated[auth.AuthUser, Depends(auth.get_current_user)]):
    return current_user


# OAuth2 Security scheme with scope https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/#oauth2-security-scheme
# Need to choose optional attribute scopes=["status"] under Login process, then scope list added to JWT token
# It is just example - in fact we don't need use scope Security for this endpoint...
@app.get("/user/status/", tags=["Authentication"])
async def read_system_status(current_user: auth.Annotated[auth.AuthUser, auth.Security(auth.get_current_active_user,
                                                                                       scopes=["status"])]):
    return {"status": "ok"}


""" Ticket ---------------------------------------------------------------------------------------------------- """

@app.post("/employee/{employee_id}/ticket/", response_model=schemas.Ticket, tags=["Ticket"])
async def create_ticket_for_employee(employee_id: int, ticket: schemas.TicketCreate, db: Session = Depends(get_db),
                                     permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["POST_ticket"]))):
    return crud.create_ticket(db=db, ticket=ticket, user_id=employee_id)


@app.get("/tickets/", response_model=list[schemas.Ticket], tags=["Ticket"])
async def read_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                       permission: bool = Depends(auth.RBAC(acl=PERMISSIONS["GET_ticket"]))):
    items = crud.get_ticket(db, skip=skip, limit=limit)
    return items
