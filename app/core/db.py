import os

from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import (
    BusinessType,
    BusinessTypeCreate,
    Country,
    CountryCreate,
    Location,
    LocationCreate,
    User,
    UserCreate,
)


def get_url():
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "30062003")
    server = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    db = os.getenv("PGDATABASE", "test_google")
    return f"postgresql+psycopg://{user}:{password}@{server}:{port}/{db}"


engine = create_engine(get_url())


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-template/issues/28


def fixtures(session: Session) -> None:
    BUSINESS_TYPES = [
        "Roofing",
        "Plumbing",
        "Electrical",
        "Carpentry",
        "Painting",
        "Landscaping",
        "Cleaning",
        "HVAC",
        "Pest Control",
        "General Contracting",
        "Flooring",
        "Masonry",
        "Drywall",
        "Fencing",
        "Concrete",
        "Demolition",
        "Excavation",
        "Insulation",
        "Siding",
    ]

    COUNTRIES = ["United States"]
    LOCATIONS = [
        "Texas",
        "California",
        "Florida",
        "New York",
        "Illinois",
        "Pennsylvania",
        "Ohio",
        "Georgia",
        "North Carolina",
        "Michigan",
        "New Jersey",
        "Virginia",
        "Washington",
        "Arizona",
        "Massachusetts",
        "Tennessee",
        "Indiana",
        "Missouri",
        "Maryland",
        "Wisconsin",
        "Colorado",
        "Minnesota",
        "South Carolina",
        "Alabama",
        "Louisiana",
        "Kentucky",
        "Oregon",
        "Oklahoma",
        "Connecticut",
        "Iowa",
        "Mississippi",
        "Arkansas",
        "Utah",
        "Kansas",
        "Nevada",
        "New Mexico",
        "Nebraska",
        "West Virginia",
        "Idaho",
        "Hawaii",
        "Maine",
        "New Hampshire",
        "Montana",
        "Rhode Island",
        "Delaware",
        "South Dakota",
        "North Dakota",
        "Alaska",
        "Vermont",
        "Wyoming",
    ]

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

    businesses = session.exec(select(BusinessType)).all()
    if not businesses:
        for business_type in BUSINESS_TYPES:
            business_in = BusinessTypeCreate(name=business_type)
            db_obj = BusinessType.model_validate(business_in)
            session.add(db_obj)

    countries = session.exec(select(Country)).all()
    if not countries:
        for country in COUNTRIES:
            country_in = CountryCreate(name=country)
            db_obj = Country.model_validate(country_in)
            session.add(db_obj)

    locations = session.exec(select(Location)).all()
    if not locations:
        for location in LOCATIONS:
            location_in = LocationCreate(name=location)
            db_obj = Location.model_validate(location_in)
            session.add(db_obj)

    session.commit()


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # from app.core.engine import engine
    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    fixtures(session)
