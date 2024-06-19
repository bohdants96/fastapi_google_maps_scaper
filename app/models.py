import re
from datetime import datetime

from pydantic import field_validator
from sqlalchemy import JSON, CheckConstraint, Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel


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

MAX_FREE_BUSINESS_LEADS = 250


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    credits: "Credit" = Relationship(back_populates="user")
    free_credit: int = Field(default=250, nullable=True)
    transactions: list["Transaction"] = Relationship(back_populates="user")
    reserved_credits: list["ReservedCredit"] = Relationship(
        back_populates="user"
    )

    scraper_events: list["ScraperEventData"] = Relationship(
        back_populates="user"
    )

    @property
    def available_credit(self) -> int:
        if not self.credits and self.free_credit <= 0:
            return 0

        if self.credits:
            return (
                self.credits.available_credit
                + self.free_credit
                - self.reserved_credit
            )
        else:
            return self.free_credit - self.reserved_credit

    @property
    def reserved_credit(self) -> int:
        if not self.reserved_credits:
            return 0

        return sum(
            reserved.credits_reserved
            for reserved in self.reserved_credits
            if reserved.status == "reserved" and reserved.credits_reserved
        )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int
    available_credit: int
    reserved_credit: int


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


class BusinessLeadBase(SQLModel):
    # scraped data related fields
    company_name: str
    company_address: str
    company_phone: str
    website: str | None = None


class BusinessLead(BusinessLeadBase, table=True):
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
    received_date: datetime


class BusinessLeadPublic(BusinessLeadBase):
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
class BusinessLeadInternal(BusinessLeadBase):
    business_type: str
    state: str | None = None
    country: str
    city: str
    county: str | None = None
    zip_code: str | None
    scraped_date: datetime


class CreditBase(SQLModel):
    user_id: int | None = Field(default=None, foreign_key="user.id")
    total_credit: int = Field(default=0, nullable=False)
    used_credit: int = Field(default=0, nullable=False)


class Credit(CreditBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int | None = Field(default=None, foreign_key="user.id")
    total_credit: int = Field(default=0, nullable=False)
    used_credit: int = Field(default=0, nullable=False)

    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())

    user: User = Relationship(back_populates="credits")

    @property
    def available_credit(self):
        return self.total_credit - self.used_credit


class TransactionBase(SQLModel):
    amount: float = Field(default=0.00, nullable=False)
    currency: str = Field(max_length=3, nullable=False)
    status: str = Field(max_length=50, nullable=False)


class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    stripe_payment_id: str = Field(
        index=True, unique=True, max_length=255, nullable=False
    )
    created_at: datetime = Field(default=datetime.now(), nullable=False)
    user: User = Relationship(back_populates="transactions")


class TransactionCreate(SQLModel):
    user_id: int
    stripe_payment_id: str
    amount: float
    currency: str
    status: str


class WebhookEventBase(SQLModel):
    event_id: str = Field(unique=True, max_length=255, nullable=False)
    event_type: str = Field(max_length=50, nullable=False)
    data: dict = Field(default_factory=dict, sa_column=Column(JSON))


class WebhookEvent(WebhookEventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now(), nullable=False)


class ReservedCreditBase(SQLModel):
    credits_reserved: int | None = Field(default=None, nullable=False)
    task_id: str | None = Field(default=None, nullable=False)
    status: str = Field(nullable=False, max_length=50)


class ReservedCredit(ReservedCreditBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default=datetime.now(), nullable=False)
    updated_at: datetime = Field(default=datetime.now(), nullable=False)
    user: User = Relationship(back_populates="reserved_credits")

    __table_args__ = (
        CheckConstraint(
            "status IN ('reserved', 'released', 'returned')",
            name="status_check",
        ),
    )


class CreatePaymentIntent(SQLModel):
    credits: int
    amount: float


class ScrapingDataRequest(SQLModel):
    businesses: list[str]
    cities: list[str] | None
    states: list[str] | None
    limit: int
    email: str


class InternalScrapingDataRequest(ScrapingDataRequest):
    internal_id: int


class ScraperEventBase(SQLModel):
    task_id: str | None = None
    status: str
    scraped_results: int | None = None
    total_results: int | None = None


class ScraperEventData(ScraperEventBase, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")

    user: User = Relationship(back_populates="scraper_events")


class ScraperEventCreate(ScraperEventBase):
    user_id: int


class ScraperEventUpdate(SQLModel):
    task_id: str | None
    status: str | None
    scraped_results: int | None
    total_results: int | None


class BusinessType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


class BusinessTypeCreate(SQLModel):
    name: str


class PublicBusinessType(SQLModel):
    id: int
    name: str
