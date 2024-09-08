from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from . import models, schemas, database
from .auth import get_password_hash
from util import get_config, get_permissions, raise_http_error, get_current_time_utc

APP_CONFIG = get_config()
PERMISSIONS = get_permissions()

""" Users -------------------------------------------------------------------------------------------------------- """


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def validate_user_role(user: schemas.UserCreate):
    # Check role is existed
    if hasattr(user, 'role'):
        # Remove role list duplication like ["admin", "admin"] and do list sorting
        user.role = list(set(user.role))
        user.role.sort(reverse=False)
        for role in user.role:
            if role not in PERMISSIONS["rbac_roles"]:
                raise_http_error(APP_CONFIG["raise_error"]["unknown_role"])

    return user


def create_user(db: Session, user: schemas.UserCreate):
    # Validate User's role(s)
    user = validate_user_role(user=user)

    # Create hashed password based on PWD_CONTEXT
    hashed_password = get_password_hash(user.password)

    # We can do record setup in a short way like:
    # https://docs.pydantic.dev/latest/concepts/serialization/#advanced-include-and-exclude
    db_user = models.User(**user.model_dump(exclude={"password"}), hashed_password=hashed_password)
    # Also we can do record setup in a long way but more clearly in detail like:
    # db_user = models.User(username=user.username,
    #                       first_name=user.first_name,
    #                       last_name=user.last_name,
    #                       phone=user.phone,
    #                       email=user.email,
    #                       role=user.role,
    #                       disabled=user.disabled,
    #                       login_denied=user.login_denied,
    #                       hashed_password=hashed_password,
    #                       created=util.get_current_time_utc("TIME"))

    db_user = database.create_db_record(db=db, db_record=db_user)
    return db_user


def update_user(db: Session, user_id, user):
    # Check if User exists
    db_user = get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise_http_error(APP_CONFIG["raise_error"]["user_not_found"])

    # Validate User's role(s)
    user = validate_user_role(user=user)

    # Update User record in database
    db_employee = database.update_db_record(db=db, db_record=db_user, payload=user)
    return db_employee


def update_user_password(db: Session, user_id, user):
    # Check if User exists
    db_user = get_user_by_id(db=db, user_id=user_id)
    if db_user is None:
        raise_http_error(APP_CONFIG["raise_error"]["user_not_found"])

    # Set new password
    db_user.hashed_password = get_password_hash(user.password)  # Create hashed password based on PWD_CONTEXT

    # Set update time-date
    db_user.updated = get_current_time_utc("TIME")

    # Update database
    db.commit()
    db.refresh(db_user)

    return JSONResponse(content={"message": APP_CONFIG["message"]["password_changed_successfully"]})


def delete_user(db: Session, user_id):
    # Check if User exists
    db_user = get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise_http_error(APP_CONFIG["raise_error"]["user_not_found"])

    # Delete User in database
    db.delete(db_user)
    db.commit()

    return JSONResponse(content={"message": APP_CONFIG["message"]["user_deleted_successfully"]})


def get_users(db: Session, skip: int = 0, limit: int = APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]):
    if limit > APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]:
        limit = APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]
    return db.query(models.User).offset(skip).limit(limit).all()


""" Employees -------------------------------------------------------------------------------------------------- """


def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def get_employee_by_email(db: Session, email: str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()  # type: ignore[call-arg]


def get_employee_by_phone(db: Session, phone: str):
    return db.query(models.Employee).filter(models.Employee.phone == phone).first()  # type: ignore[call-arg]


def get_employees(db: Session, skip: int = 0, limit: int = APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]):
    if limit > APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]:
        limit = APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]
    return db.query(models.Employee).offset(skip).limit(limit).all()


def create_employee(db: Session, employee: schemas.EmployeeCreate):
    # We can do record setup in a short way like:
    db_employee = models.Employee(**employee.model_dump(), created=get_current_time_utc("TIME"))
    # Also we can do record setup in a long way but more clearly in detail like:
    # db_employee = models.Employee(first_name=employee.first_name,
    #                               last_name=employee.last_name,
    #                               nick_name=employee.nick_name,
    #                               phone=employee.phone,
    #                               email=employee.email,
    #                               birthday=str(employee.birthday),
    #                               country=employee.country,
    #                               city=employee.city,
    #                               address=employee.address,
    #                               created=util.get_current_time_utc("TIME"))

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, employee_id, employee):
    # Check if Employee exists
    db_employee = get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise_http_error(APP_CONFIG["raise_error"]["employee_not_found"])

    # Update Employee record in database
    db_employee = database.update_db_record(db, db_employee, employee)
    return db_employee


def delete_employee(db: Session, employee_id):
    # Check if Employee exists
    db_employee = get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise_http_error(APP_CONFIG["raise_error"]["employee_not_found"])

    # Delete User in database
    db.delete(db_employee)
    db.commit()

    # Response Model - Return Type
    # https://fastapi.tiangolo.com/tutorial/response-model/?h=#response-model-return-type
    return JSONResponse(content={"message": APP_CONFIG["message"]["employee_deleted_successfully"]})


""" Tickets ---------------------------------------------------------------------------------------------------- """


def create_ticket(db: Session, ticket: schemas.TicketCreate, user_id: int, employee_id: int):
    db_item = models.Ticket(**ticket.model_dump(),
                            owner_id=user_id,
                            employee_id=employee_id,
                            created=get_current_time_utc("TIME"))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_tickets(db: Session, skip: int = 0, limit: int = APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]):
    if limit > APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]:
        limit = APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]
    return db.query(models.Ticket).offset(skip).limit(limit).all()


def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()


def get_my_tickets(db: Session, owner_id: int, skip: int = 0, limit: int = APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]):
    if limit > APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]:
        limit = APP_CONFIG["BODY_RESPONSE_ITEMS_LIMIT"]
    return db.query(models.Ticket).filter(models.Ticket.owner_id == owner_id).offset(skip).limit(limit).all()


def update_ticket(db: Session, db_ticket, ticket: schemas.TicketUpdate):
    # Update Ticket record in database
    db_ticket = database.update_db_record(db=db, db_record=db_ticket, payload=ticket)
    return db_ticket
