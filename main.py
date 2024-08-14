"""
RESTful OpenAPI Specification (OAS) application programming interface (API) based on FastAPI framework
Documentation: api-url/docs
"""
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import util
from sql_app import crud, models, schemas, auth
from sql_app.database import engine, get_db

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


@app.get('/favicon.ico', include_in_schema=False)  # Exclude request from DOCS schema
async def favicon():
    # https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse
    return FileResponse("./static/favicon.ico")


# Create (POST)
@app.post("/user/", response_model=schemas.User, tags=["Users"])
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),
                      permission: bool = Depends(auth.RBAC(acl=["admin"]))):
    # Check if unique user's identification attributes already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered!")

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered!")

    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered!")

    return crud.create_user(db=db, user=user)


# Create (POST)
@app.post("/employee/", response_model=schemas.Employee, tags=["Employee"])
async def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db),
                          permission: bool = Depends(auth.RBAC(acl=["admin", "manager"]))):
    # Check if unique employee's identification attributes already exists
    db_employee = crud.get_employee_by_email(db, email=employee.email)
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered!")

    db_employee = crud.get_employee_by_phone(db, phone=employee.phone)
    if db_employee:
        raise HTTPException(status_code=400, detail="Phone already registered!")

    return crud.create_employee(db=db, employee=employee)


# Read (GET)
@app.get("/employee/{employee_id}", response_model=schemas.Employee, tags=["Employee"])
async def read_employee(employee_id: int, db: Session = Depends(get_db),
                        permission: bool = Depends(auth.RBAC(acl=["admin", "manager", "users:read"]))):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="User not found!")
    return db_employee


# Update (PUT)
@app.put("/employee/{employee_id}", response_model=schemas.Employee, tags=["Employee"])
async def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db),
                          permission: bool = Depends(auth.RBAC(acl=["admin", "manager"]))):
    # Check if Employee exists
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found!")

    return crud.update_employee(db=db, db_employee=db_employee, employee=employee)


# Delete (DELETE)
@app.delete("/employee/{employee_id}", tags=["Employee"])
async def delete_employee(employee_id: int, db: Session = Depends(get_db),
                          permission: bool = Depends(auth.RBAC(acl=["admin", "manager"]))):
    # Check if Employee exists
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found!")

    return crud.delete_employee(db=db, db_employee=db_employee)


@app.get("/employee/", response_model=list[schemas.Employee], tags=["Employee"])
async def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    employees = crud.get_employees(db, skip=skip, limit=limit)
    return employees


@app.post("/users/{user_id}/items/", response_model=schemas.Item, tags=["Items"])
async def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item], tags=["Items"])
async def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


""" OAuth2PasswordRequestForm:
This is a dependency class to collect the `username` and `password` as form data for an OAuth2 password flow.
The OAuth2 specification dictates that for a password flow the data should be collected using form data 
(instead of JSON) and that it should have the specific fields `username` and `password`.
"""


@app.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: auth.Annotated[auth.OAuth2PasswordRequestForm, Depends()],
                                 db: Session = Depends(get_db)
                                 ) -> auth.Token:

    db_user = crud.get_user_by_username(db, username=form_data.username)
    user = auth.authenticate_user(db_user, form_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect User's name or password")
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return auth.Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=auth.AuthUser, tags=["Authentication"])
async def read_users_me(current_user: auth.Annotated[auth.AuthUser, Depends(auth.get_current_user)]):
    return current_user


@app.get("/status/", tags=["Authentication"])
async def read_system_status(current_user: auth.Annotated[auth.AuthUser, Depends(auth.get_current_active_user)]):
    return {"status": "ok"}
