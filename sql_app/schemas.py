"""
https://stackoverflow.com/questions/71570607/sqlalchemy-models-vs-pydantic-models
https://docs.pydantic.dev/latest/
    Pydantic is the most widely used data validation library for Python. Fast and extensible, Pydantic plays nicely
with your linters/IDE/brain. Define how data should be in pure and Python canonical - validate it with Pydantic.
    SQLAlchemy is responsible for db models (should reflect the structure of your database). SQLAlchemy and many others
are by default "lazy loading". That means, for example, that they don't fetch the data for relationships from the
database unless you try to access the attribute that would contain that data.
    But with ORM mode, as Pydantic itself will try to access the data it needs from attributes (instead of assuming
a dict), you can declare the specific data you want to return and it will be able to go and get it, even from ORMs.
    Pydantic should be responsible for schemas (basically defining input and output formats) and DTOs (used to
transfer data between different layers of an app).
"""
from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True
