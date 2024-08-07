"""
https://fastapi.tiangolo.com/tutorial/sql-databases/#sql-relational-databases
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import util

SQLALCHEMY_DATABASE_URL = f"sqlite:////{util.get_project_root()}{util.get_config()['sqlite_db_path']}"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    # connect_args is needed only for SQLite. It's not needed for other databases!
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
