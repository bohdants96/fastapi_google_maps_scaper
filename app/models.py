import re
from datetime import datetime, timedelta

from phonenumbers import (
    NumberParseException,
    PhoneNumberFormat,
    PhoneNumberType,
    format_number,
    is_valid_number,
    number_type,
    parse as parse_phone_number,
)
from pydantic import AnyHttpUrl, field_validator
from sqlalchemy import JSON, CheckConstraint, Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

MOBILE_NUMBER_TYPES = (
    PhoneNumberType.MOBILE,
    PhoneNumberType.FIXED_LINE_OR_MOBILE,
)


# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None
    mobile_phone: str | None = None
    instagram: str | None = None
    twitter: str | None = None
    facebook: str | None = None
    linkedin: str | None = None
    avatar_url: str | None = None
    last_password_reset_time: datetime | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    instagram: AnyHttpUrl | None = None
    twitter: AnyHttpUrl | None = None
    facebook: AnyHttpUrl | None = None
    linkedin: AnyHttpUrl | None = None
    avatar_url: AnyHttpUrl | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserRegister(SQLModel):
    email: str
    password: str
    full_name: str | None = None
    mobile_phone: str | None = None
    instagram: AnyHttpUrl | None = None
    twitter: AnyHttpUrl | None = None
    facebook: AnyHttpUrl | None = None
    linkedin: AnyHttpUrl | None = None
    avatar_url: AnyHttpUrl | None = None

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

    @field_validator("mobile_phone")
    def check_phone_number(cls, v):
        if v is None:
            return v

        try:
            n = parse_phone_number(v)
        except NumberParseException as e:
            raise ValueError(
                "Please provide a valid mobile phone number"
            ) from e

        if not is_valid_number(n) or number_type(n) not in MOBILE_NUMBER_TYPES:
            raise ValueError("Please provide a valid mobile phone number")

        return format_number(
            n,
            (
                PhoneNumberFormat.NATIONAL
                if n.country_code == 44
                else PhoneNumberFormat.INTERNATIONAL
            ),
        )


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None
    mobile_phone: str | None = None
    instagram: AnyHttpUrl | None = None
    twitter: AnyHttpUrl | None = None
    facebook: AnyHttpUrl | None = None
    linkedin: AnyHttpUrl | None = None
    avatar_url: AnyHttpUrl | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None
    mobile_phone: str | None = None
    instagram: AnyHttpUrl | None = None
    twitter: AnyHttpUrl | None = None
    facebook: AnyHttpUrl | None = None
    linkedin: AnyHttpUrl | None = None
    avatar_url: AnyHttpUrl | None = None

    @field_validator("email")
    def email_must_be_valid(cls, value):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_regex, value):
            raise ValueError("Invalid email address")

        return value

    @field_validator("mobile_phone")
    def check_phone_number(cls, v):
        if v is None:
            return v

        try:
            n = parse_phone_number(v)
        except NumberParseException as e:
            raise ValueError(
                "Please provide a valid mobile phone number"
            ) from e

        if not is_valid_number(n) or number_type(n) not in MOBILE_NUMBER_TYPES:
            raise ValueError("Please provide a valid mobile phone number")

        return format_number(
            n,
            (
                PhoneNumberFormat.NATIONAL
                if n.country_code == 44
                else PhoneNumberFormat.INTERNATIONAL
            ),
        )


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
    last_password_reset_time: datetime | None = Field(default=None)
    transactions: list["Transaction"] = Relationship(back_populates="user")
    reserved_credits: list["ReservedCredit"] = Relationship(
        back_populates="user"
    )

    scraper_events: list["ScraperEventData"] = Relationship(
        back_populates="user"
    )

    search_history: list["SearchHistory"] = Relationship(back_populates="user")

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

    @property
    def credit_usage(self) -> int:
        if not self.search_history:
            return 0

        current_month_start = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        next_month = current_month_start.replace(
            month=current_month_start.month % 12 + 1
        )
        current_month_end = next_month - timedelta(seconds=1)

        return sum(
            action.credits_used
            for action in self.search_history
            if current_month_start <= action.search_time <= current_month_end
        )

    @property
    def leads_collected(self) -> int:
        if not self.search_history:
            return 0

        current_month_start = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        next_month = current_month_start.replace(
            month=current_month_start.month % 12 + 1
        )
        current_month_end = next_month - timedelta(seconds=1)

        return sum(
            action.credits_used
            for action in self.search_history
            if current_month_start <= action.search_time <= current_month_end
        )

    @property
    def money_spent(self) -> int:
        if not self.transactions:
            return 0

        current_month_start = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        next_month = current_month_start.replace(
            month=current_month_start.month % 12 + 1
        )
        current_month_end = next_month - timedelta(seconds=1)

        return sum(
            transaction.amount
            for transaction in self.transactions
            if transaction.status == "succeeded"
            and current_month_start
            <= transaction.created_at
            <= current_month_end
        )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int
    available_credit: int
    reserved_credit: int
    credit_usage: int
    leads_collected: int
    money_spent: int


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
    last_password_reset_time: datetime


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


class PublicTransaction(SQLModel):
    id: int
    user_id: int
    stripe_payment_id: str
    amount: float
    currency: str
    status: str
    created_at: datetime


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


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    full_name: str = Field(nullable=False)
    subject: str | None = Field(default=None)
    company_name: str | None = Field(default=None)
    mobile_phone: str | None = Field(default=None)
    email: str = Field(nullable=False, index=True)
    message: str = Field(nullable=False)


class TicketRequest(SQLModel):
    full_name: str = Field(nullable=False)
    subject: str | None = Field(default=None)
    company_name: str | None = Field(default=None)
    mobile_phone: str | None = Field(default=None)
    email: str = Field(nullable=False, index=True)
    message: str = Field(nullable=False)

    @field_validator("email")
    def email_must_be_valid(cls, value):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_regex, value):
            raise ValueError("Invalid email address")

        return value

    @field_validator("mobile_phone")
    def check_phone_number(cls, v):
        if v is None:
            return v

        try:
            n = parse_phone_number(v)
        except NumberParseException as e:
            raise ValueError(
                "Please provide a valid mobile phone number"
            ) from e

        if not is_valid_number(n) or number_type(n) not in MOBILE_NUMBER_TYPES:
            raise ValueError("Please provide a valid mobile phone number")

        return format_number(
            n,
            (
                PhoneNumberFormat.NATIONAL
                if n.country_code == 44
                else PhoneNumberFormat.INTERNATIONAL
            ),
        )


class SearchHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    search_time: datetime = Field(default=datetime.now())
    internal_search_ids: dict = Field(sa_column=Column(JSON))
    credits_used: int = Field(default=0)
    source: str = Field(default=None)

    user: User = Relationship(back_populates="search_history")


class SearchHistoryCreate(SQLModel):
    internal_search_ids: dict
    credits_used: int
    user_id: int
    source: str


class PublicSearchHistory(SQLModel):
    id: int
    user_id: int
    internal_search_ids: dict
    credits_used: int
    source: str
    search_time: datetime
