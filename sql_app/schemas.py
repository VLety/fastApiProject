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
        # orm_mode = True  # Pydantic V1 version format -> 'orm_mode' has been renamed to 'from_attributes'
        from_attributes = True  # Pydantic V2 version


class UserBase(BaseModel):
    # Make Input json based on current (main) class
    first_name: str
    last_name: str
    nick_name: str
    phone: str
    email: str
    birthday: str
    country: str
    city: str
    address: str


class UserCreate(UserBase):
    # Make Input json based on main UserBase(BaseModel) class + current class
    #  password: str  # We can add here additional parameter that is not present in UserBase Class
    pass


class User(UserBase):
    # Make Output json based on main UserBase(BaseModel) class + current class
    id: int
    created: str
    updated: str | None = None  # | None = None options required if no value present in database
    items: list[Item] = []

    class Config:
        # orm_mode = True  # Pydantic V1 version format -> 'orm_mode' has been renamed to 'from_attributes'
        from_attributes = True  # Pydantic V2 version
