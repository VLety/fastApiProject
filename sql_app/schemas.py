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
from pydantic import BaseModel, Field, ValidationError, ValidationInfo, model_validator
from typing import Optional
from typing_extensions import Self
import re
import util

APP_SCHEMAS = util.get_schemas()
PERMISSIONS = util.get_permissions()

""" Authorization -------------------------------------------------------------------------------------------------- """

class AuthToken(BaseModel):
    access_token: str
    token_type: str


class AuthTokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


""" Users ---------------------------------------------------------------------------------------------------------- """

class UserUsernameAttr(BaseModel):
    username: str = Field(
        min_length=APP_SCHEMAS["User"]["username"]["min_length"],
        max_length=APP_SCHEMAS["User"]["username"]["max_length"],
        examples=APP_SCHEMAS["User"]["username"]["examples"],
        pattern=APP_SCHEMAS["User"]["username"]["pattern"],
    )


class UserPasswordAttr(BaseModel):
    password: str = Field(min_length=APP_SCHEMAS["User"]["password"]["min_length"],
                          max_length=APP_SCHEMAS["User"]["password"]["max_length"],
                          examples=APP_SCHEMAS["User"]["password"]["examples"],
                          )

    # Model validators: https://docs.pydantic.dev/latest/concepts/validators/#model-validators
    @model_validator(mode='after')
    def check_passwords(self) -> Self:
        for pattern in APP_SCHEMAS["User"]["password"]["pattern"]:
            if re.search(pattern["regex"], self.password) is None:
                raise ValueError(pattern["error"] + ": " + pattern["regex"])
        return self


class UserContactsAttr(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str


class UserRoleAttr(BaseModel):
    role: list[str] = Field(examples=[PERMISSIONS["rbac_roles"]])


class UserDisabledAttr(BaseModel):
    disabled: bool = Field(default=False)


class UserLoginDeniedAttr(BaseModel):
    login_denied: bool = Field(default=False)


class UserSecureAttr(UserLoginDeniedAttr, UserDisabledAttr, UserRoleAttr):
    # Class created from parent classes by "stack (LIFO) principle": first class will be most bottom.
    pass


class UserBase(UserSecureAttr, UserContactsAttr, UserUsernameAttr):
    # Class created from parent classes by "stack (LIFO) principle": first class will be most bottom.
    pass


class UserCreate(UserSecureAttr, UserContactsAttr, UserPasswordAttr, UserUsernameAttr):
    # Class created from parent classes by "stack (LIFO) principle": first class will be most bottom.
    pass


class UserContactsUpdate(UserContactsAttr):
    first_name: Optional[str] | None = None
    last_name: Optional[str] | None = None
    phone: Optional[str] | None = None
    email: Optional[str] | None = None


class UserResponse(UserBase):
    # Make Output json based on parent UserBase(BaseModel) class + current class
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
    description: str
    status: str


class TicketCreate(TicketBase):
    pass


class Ticket(TicketBase):
    id: int
    owner_id: int
    employee_id: int

    class Config:
        # orm_mode = True  # Pydantic V1 version format -> 'orm_mode'
        from_attributes = True  # Pydantic V2 version


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


class EmployeeResponse(EmployeeBase):
    # Output response json based on main EmployeeBase(BaseModel) class + current class
    id: int
    created: str
    updated: str | None = None  # | None = None options required if no value present in database
    tickets: list[Ticket] = []

    class Config:
        # orm_mode = True  # Pydantic V1 version format -> 'orm_mode' has been renamed to 'from_attributes'
        from_attributes = True  # Pydantic V2 version
