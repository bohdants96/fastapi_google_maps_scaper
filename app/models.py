import re
from datetime import datetime

from sqlmodel import Field, SQLModel
from pydantic import field_validator, ValidationError


# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserRegister(SQLModel):
    email: str
    password: str
    full_name: str | None = None

    @field_validator("email")
    def email_must_be_valid(cls, value):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_regex, value):
            raise ValueError("Invalid email address")

        return value

    @field_validator("password")
    def password_must_be_valid(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 8 characters long")

        if len(value) > 20:
            raise ValueError("Password must be at most 20 characters long")

        return value


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str


class ScrapedDataBase(SQLModel):
    # scraped data related fields
    company_name: str
    company_address: str
    company_phone: str
    website: str | None = None


class ScrapedData(ScrapedDataBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    business_type: str = Field(index=True)

    # location related fields
    state: str | None = Field(index=True)
    country: str = Field(index=True)
    city: str = Field(index=True)
    county: str | None = None
    zip_code: str | None

    # date related fields
    scraped_date: datetime
    received_date: datetime = Field(default=datetime.now())


class ScrapedDataPublic(ScrapedDataBase):
    id: int
    business_type: str
    state: str | None = None
    country: str
    city: str
    county: str | None = None
    zip_code: str | None
    scraped_date: datetime
    received_date: datetime


# Internal Scraped Data
class ScrapedDataInternal(ScrapedDataBase):
    business_type: str
    state: str | None = None
    country: str
    city: str
    county: str | None = None
    zip_code: str | None
    scraped_date: datetime
