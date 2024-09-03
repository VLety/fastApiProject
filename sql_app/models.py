"""
https://docs.sqlalchemy.org/en/20/dialects/sqlite.html
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, MetaData
from sqlalchemy.orm import relationship
from .database import Base
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
    __tablename__ = "users"  # Set relevant table name or skip this string if class name is equal table name
    metadata_obj = metadata_obj  # Create table if not exist

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

    tickets = relationship("Ticket", back_populates="owner")  # Set table relation


class Employee(Base):
    __tablename__ = "employees"  # Set relevant table name or skip this string if class name is equal table name
    metadata_obj = metadata_obj  # Create table if not exist

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

    tickets = relationship("Ticket", back_populates="employee")  # Set table relation


class Ticket(Base):
    __tablename__ = "tickets"  # Set relevant table name or skip this string if class name is equal table name
    metadata_obj = metadata_obj  # Create table if not exist

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    status = Column(String, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    employee = relationship("Employee", back_populates="tickets")  # Set table relation
    owner = relationship("User", back_populates="tickets")  # Set table relation
