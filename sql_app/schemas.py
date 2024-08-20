"""
https://stackoverflow.com/questions/71570607/sqlalchemy-models-vs-pydantic-models
https://docs.pydantic.dev/latest/
    Pydantic is the most widely used data validation library for Python. Fast and extensible, Pydantic plays nicely
with your linters/IDE/brain. Define how data should be in pure and Python canonical - validate it with Pydantic.
    SQLAlchemy is responsible for db models (should reflect the structure of your database). SQLAlchemy and many others
are by default "lazy loading". That means, for example, that they don't fetch the data for relationships from the
database unless you try to access the attribute that would contain that data.
    But with ORM mode, as Pydantic itself will try to access the data it needs from attributes (instead of assuming
a dict), you can declare the specific data you want to return, and it will be able to go and get it, even from ORMs.
    Pydantic should be responsible for schemas (basically defining input and output formats) and DTOs (used to
transfer data between different layers of an app).
"""
from datetime import date
from pydantic import BaseModel, Field


""" Authorization -------------------------------------------------------------------------------------------------- """
class AuthUser(BaseModel):
    id: int
    username: str
    email: str | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: list[str] = []
    disabled: bool | None = None
    login_denied: bool | None = None

class AuthUserInDB(AuthUser):
    hashed_password: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str

class AuthTokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


""" Users ---------------------------------------------------------------------------------------------------------- """
class UserBase(BaseModel):
    # Make Input json based on current (main) class
    username: str = Field(pattern=r"^[0-9A-Za-z]$", min_length=5, max_length=16)
    first_name: str
    last_name: str
    phone: str
    email: str
    role: list[str]
    disabled: bool = Field(default=False)
    login_denied: bool = Field(default=False)

class UserCreate(UserBase):
    # Make Input json based on main UserBase(BaseModel) class + current class
    # password: str  # We can add here additional parameter that is not present in UserBase Class
    password: str = Field(min_length=8, max_length=16)


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str


class UserRoleUpdate(BaseModel):
    role: list[str]


class UserResponse(UserBase):
    # Make Output json based on main UserBase(BaseModel) class + current class
    id: int
    created: str
    updated: str | None = None  # | None = None options required if no value present in database

    class Config:
        # orm_mode = True  # Pydantic V1 version format -> 'orm_mode' has been renamed to 'from_attributes'
        from_attributes = True  # Pydantic V2 version


""" Employees + Tickets -------------------------------------------------------------------------------------------- """
class EmployeeBase(BaseModel):
    # Make Input json based on current (main) class
    first_name: str
    last_name: str
    nick_name: str
    phone: str
    email: str
    birthday: date
    country: str
    city: str
    address: str

class EmployeeCreate(EmployeeBase):
    # Make Input json based on main EmployeeBase(BaseModel) class + current class
    # password: str  # We can add here additional parameter that is not present in UserBase Class
    pass

class EmployeeUpdate(BaseModel):
    # Make Input json based on main EmployeeBase(BaseModel) class + current class
    # password: str  # We can add here additional parameter that is not present in UserBase Class
    first_name: str | None = None
    last_name: str | None = None
    nick_name: str | None = None
    phone: str | None = None
    email: str | None = None
    birthday: date = None
    country: str | None = None
    city: str | None = None
    address: str | None = None

class TicketBase(BaseModel):
    title: str
    description: str | None = None
    status: str

class TicketCreate(TicketBase):
    pass

class Ticket(TicketBase):
    id: int
    owner_id: int

    class Config:
        # orm_mode = True  # Pydantic V1 version format -> 'orm_mode' has been renamed to 'from_attributes'
        from_attributes = True  # Pydantic V2 version

class EmployeeResponse(EmployeeBase):
    # Output response json based on main EmployeeBase(BaseModel) class + current class
    id: int
    created: str
    updated: str | None = None  # | None = None options required if no value present in database
    tickets: list[Ticket] = []

    class Config:
        # orm_mode = True  # Pydantic V1 version format -> 'orm_mode' has been renamed to 'from_attributes'
        from_attributes = True  # Pydantic V2 version


