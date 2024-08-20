from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from . import models, schemas
import util

APP_CONFIG = util.get_config()
PERMISSIONS = util.get_permissions()  # Project access permission data

""" Users ---------------------------------------------------------------------------------------------------------- """

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()  # type: ignore[call-arg]


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()  # type: ignore[call-arg]


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()  # type: ignore[call-arg]


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()  # type: ignore[call-arg]


def check_new_user(db: Session, user: schemas.UserCreate):
    # Check if User's role is allowed
    for role in user.role:
        if role not in PERMISSIONS["rbac_roles"]:
            raise HTTPException(status_code=400, detail=APP_CONFIG["raise_error"]["unknown_role"])

    # Check if unique User's identification attributes already exists
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


def update_user(db: Session, user_id, user):
    # Check if User exists
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=APP_CONFIG["raise_error"]["user_not_found"])

    # Update User record in database
    db_employee = update_db_record_by_id(db, db_user, user)
    return db_employee


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


""" Employees + Tickets -------------------------------------------------------------------------------------------- """

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
                                  birthday=str(employee.birthday),
                                  country=employee.country,
                                  city=employee.city,
                                  address=employee.address,
                                  created=util.get_current_time_utc("TIME"))
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, employee_id, employee):
    # Check if Employee exists
    db_employee = get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail=APP_CONFIG["raise_error"]["employee_not_found"])

    # Update Employee record in database
    db_employee = update_db_record_by_id(db, db_employee, employee)
    return db_employee


def delete_employee(db: Session, db_employee):
    db.delete(db_employee)
    db.commit()

    # Response Model - Return Type
    # https://fastapi.tiangolo.com/tutorial/response-model/?h=#response-model-return-type
    return JSONResponse(content={"message": APP_CONFIG["message"]["employee_deleted_successfully"]})


def get_ticket(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ticket).offset(skip).limit(limit).all()


def create_ticket(db: Session, ticket: schemas.TicketCreate, user_id: int):
    db_item = models.Ticket(**ticket.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


""" Support functions -------------------------------------------------------------------------------------------- """

def update_db_record_by_id(db, db_record, payload):

    # Set new fild(s) value(s) and not override existence DB field(s)
    for field_name in payload.model_fields_set:
        setattr(db_record, field_name, getattr(payload, field_name))

    # Set update time-date
    db_record.updated = util.get_current_time_utc("TIME")

    # Update database
    db.commit()
    db.refresh(db_record)
    return db_record

