from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


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
