"""
https://docs.sqlalchemy.org/en/20/dialects/sqlite.html
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, MetaData
from sqlalchemy.orm import relationship
from .database import Base
from sql_app.database import engine, get_db
from sqlalchemy.dialects.sqlite import (
    BLOB,
    BOOLEAN,
    CHAR,
    DATE,
    DATETIME,
    DECIMAL,
    FLOAT,
    INTEGER,
    NUMERIC,
    JSON,
    SMALLINT,
    TEXT,
    TIME,
    TIMESTAMP,
    VARCHAR,
)
metadata_obj = MetaData()

class User(Base):
    __tablename__ = "users"  # Set relevant table name or pass this string if class name is equal table name
    metadata_obj = metadata_obj

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    username = Column(String(16), index=True, unique=True)
    first_name = Column(String(64), index=True)
    last_name = Column(String(64), index=True)
    phone = Column(String(20), index=True, unique=True)
    email = Column(String(254), index=True, unique=True)
    role = Column(JSON())
    disabled = Column(BOOLEAN, default=False)
    login_denied = Column(BOOLEAN, default=False)
    hashed_password = Column(VARCHAR(64))
    created = Column(VARCHAR(19), index=True)
    updated = Column(VARCHAR(19), index=True)


class Employee(Base):
    __tablename__ = "employees"  # Set relevant table name or pass this string if class name is equal table name

    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), index=True)
    last_name = Column(String(64), index=True)
    nick_name = Column(String(20), index=True)
    phone = Column(String(20), index=True, unique=True)
    email = Column(String(254), index=True, unique=True)
    birthday = Column(String(10), index=True)
    country = Column(String(64), index=True)
    city = Column(String(64), index=True)
    address = Column(String(254), index=True)
    created = Column(String(19), index=True)
    updated = Column(String(19), index=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"  # Set relevant table name or pass this string if class name is equal table name

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("employees.id"))

    owner = relationship("Employee", back_populates="items")
