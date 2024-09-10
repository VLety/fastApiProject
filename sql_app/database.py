"""
Project name: REST API server solution based on FastAPI framework with RBAC model
Author: Volodymyr Letiahin
Contact: https://www.linkedin.com/in/volodymyr-letiahin-0208a5b2/
License: MIT
"""
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from util import get_project_root, get_config, raise_http_error, get_current_time_utc

APP_CONFIG = get_config()
SQLALCHEMY_DB_PATH = f"sqlite:////{get_project_root()}{APP_CONFIG['sqlite_db_path']}"

# connect_args is needed only for SQLite. It's not needed for other databases!
engine = create_engine(SQLALCHEMY_DB_PATH, connect_args={"check_same_thread": False})

# Dependency -> We need to have an independent database session/connection (SessionLocal) per request, use the same
# session through all the request and then close it after the request is finished. And then a new session will be
# created for the next request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> SessionLocal():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def update_db_record(db: Session, db_record, payload):
    # Set new field(s) value(s) and not override existence DB field(s)
    for field_name in payload.model_fields_set:
        setattr(db_record, field_name, getattr(payload, field_name))

    # Set update time-date
    db_record.updated = get_current_time_utc("TIME")

    # Update record in database
    try:
        db.commit()
        db.refresh(db_record)
        return db_record

    except exc.IntegrityError as error:
        database_error_handler(db=db, error=error)


def create_db_record(db: Session, db_record):
    # Set created time-date
    db_record.created = get_current_time_utc("TIME")

    # Create record in database
    try:
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record

    except exc.IntegrityError as error:
        database_error_handler(db=db, error=error)


def database_error_handler(db: Session, error: exc.IntegrityError):
    # Session.rollback() method will be called so that the transaction is rolled back immediately,
    # before propagating the exception outward.
    db.rollback()

    parsed_error = str(error.orig.args[0])

    # Manage UNIQUE field errors
    if parsed_error == "UNIQUE constraint failed: users.username":
        raise_http_error(APP_CONFIG["raise_error"]["username_already_registered"])
    elif parsed_error == "UNIQUE constraint failed: users.phone":
        raise_http_error(APP_CONFIG["raise_error"]["phone_already_registered"])
    elif parsed_error == "UNIQUE constraint failed: users.email":
        raise_http_error(APP_CONFIG["raise_error"]["email_already_registered"])

    # Another error(s)
    else:
        print("SQLAlchemy IntegrityError:", parsed_error)
        raise_http_error(APP_CONFIG["raise_error"]["error_processing_database_request"])
