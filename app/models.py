from datetime import datetime

from sqlmodel import Field, SQLModel


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


class BusinessTypeBase(SQLModel):
    name: str | None = None


class CountryBase(SQLModel):
    name: str | None = None


class LocationBase(SQLModel):
    name: str | None = None


class ScrapedDataBase(SQLModel):
    company_name: str | None = None
    business_type: str | None = None
    company_address: str | None = None
    company_phone: int | None = None
    country_id: int | None = None
    location_id: int | None = None
    state: str | None = None
    zip_code: int | None = None


class BusinessType(BusinessTypeBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = None
    created_at: datetime | None = None


class Country(CountryBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = None
    created_at: datetime | None = None


class Location(LocationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = None
    created_at: datetime | None = None


class ScrapedData(ScrapedDataBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company_name: str | None = None
    business_type: str | None = None
    company_address: str | None = None
    company_phone: int | None = None
    country_id: int | None = None
    location_id: int | None = None
    state: str | None = None
    zip_code: int | None = None
    created_at: datetime | None = None


class BusinessTypeCreate(BusinessTypeBase):
    name: str | None = None


class CountryCreate(CountryBase):
    name: str | None = None


class LocationCreate(LocationBase):
    name: str | None = None


class ScrapedDataCreate(ScrapedDataBase):
    company_name: str | None = None
    business_type: str | None = None
    company_address: str | None = None
    company_phone: int | None = None
    country_id: int | None = None
    location_id: int | None = None
    state: str | None = None
    zip_code: int | None = None


class CountryPublic(CountryBase):
    id: int
    created_at: datetime | None = None


class CountriesPublic(SQLModel):
    data: list[CountryPublic]
    count: int


class LocationPublic(LocationBase):
    id: int
    created_at: datetime | None = None


class LocationsPublic(SQLModel):
    data: list[LocationPublic]
    count: int


class BusinessTypePublic(BusinessTypeBase):
    id: int
    created_at: datetime | None = None


class BusinessTypesPublic(SQLModel):
    data: list[LocationPublic]
    count: int


class ScrapedDataPublic(ScrapedDataBase):
    id: int
    location_id: int | None = None
    state: str | None = None
    created_at: datetime | None = None


class ScrapedDatasPublic(SQLModel):
    data: list[ScrapedDataPublic]
    count: int
