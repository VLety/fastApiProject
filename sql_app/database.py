from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException
import util

APP_CONFIG = util.get_config()
SQLALCHEMY_DB_PATH = f"sqlite:////{util.get_project_root()}{APP_CONFIG['sqlite_db_path']}"

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
    db_record.updated = util.get_current_time_utc("TIME")

    # Update record in database
    try:
        db.commit()
        db.refresh(db_record)
        return db_record

    except exc.IntegrityError as error:
        database_error_handler(db=db, error=error)


def create_db_record(db: Session, db_record):

    # Set created time-date
    db_record.created = util.get_current_time_utc("TIME")

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
        raise HTTPException(status_code=422, detail=APP_CONFIG["raise_error"]["username_already_registered"])
    elif parsed_error == "UNIQUE constraint failed: users.phone":
        raise HTTPException(status_code=422, detail=APP_CONFIG["raise_error"]["phone_already_registered"])
    elif parsed_error == "UNIQUE constraint failed: users.email":
        raise HTTPException(status_code=422, detail=APP_CONFIG["raise_error"]["email_already_registered"])

    # Another errors
    else:
        print("SQLAlchemy IntegrityError:", parsed_error)
        raise HTTPException(status_code=422, detail=APP_CONFIG["raise_error"]["error_processing_database_request"])