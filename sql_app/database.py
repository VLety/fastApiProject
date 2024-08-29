"""
https://fastapi.tiangolo.com/tutorial/sql-databases/#sql-relational-databases
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import util

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = f"sqlite:////{util.get_project_root()}{util.get_config()['sqlite_db_path']}"

# connect_args is needed only for SQLite. It's not needed for other databases!
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

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
