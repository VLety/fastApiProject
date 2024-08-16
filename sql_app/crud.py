from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from . import models, schemas
import util
APP_CONFIG = util.get_config()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()  # type: ignore[call-arg]


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()  # type: ignore[call-arg]


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()  # type: ignore[call-arg]


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()  # type: ignore[call-arg]


def check_new_user(db: Session, user: schemas.UserCreate):

    # Check if role is allowed
    for role in user.role:
        if role not in APP_CONFIG["auth"]["rbac_roles"]:
            raise HTTPException(status_code=400, detail=APP_CONFIG["raise_error"]["unknown_role"])

    # Check if unique user's identification attributes already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail=APP_CONFIG["raise_error"]["username_already_registered"])

    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail=APP_CONFIG["raise_error"]["email_already_registered"])

    db_user = get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail=APP_CONFIG["raise_error"]["phone_already_registered"])


def create_user(db: Session, user: schemas.UserCreate, hashed_password):
    db_user = models.User(username=user.username,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          phone=user.phone,
                          email=user.email,
                          role=user.role,
                          disabled=user.disabled,
                          login_denied=user.login_denied,
                          hashed_password=hashed_password,
                          created=util.get_current_time_utc("TIME"))

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()  # type: ignore[call-arg]


def get_employee_by_email(db: Session, email: str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()  # type: ignore[call-arg]


def get_employee_by_phone(db: Session, phone: str):
    return db.query(models.Employee).filter(models.Employee.phone == phone).first()  # type: ignore[call-arg]


def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()


def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(first_name=employee.first_name,
                                  last_name=employee.last_name,
                                  nick_name=employee.nick_name,
                                  phone=employee.phone,
                                  email=employee.email,
                                  birthday=employee.birthday,
                                  country=employee.country,
                                  city=employee.city,
                                  address=employee.address,
                                  created=util.get_current_time_utc("TIME"))
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, db_employee, employee):
    db_employee.first_name = employee.first_name
    db_employee.last_name = employee.last_name
    db_employee.nick_name = employee.nick_name
    db_employee.phone = employee.phone
    db_employee.email = employee.email
    db_employee.birthday = employee.birthday
    db_employee.country = employee.country
    db_employee.city = employee.city
    db_employee.address = employee.address
    db_employee.updated = util.get_current_time_utc("TIME")

    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, db_employee):
    db.delete(db_employee)
    db.commit()

    # Response Model - Return Type
    # https://fastapi.tiangolo.com/tutorial/response-model/?h=#response-model-return-type
    return JSONResponse(content={"message": APP_CONFIG["message"]["employee_deleted_successfully"]})


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
