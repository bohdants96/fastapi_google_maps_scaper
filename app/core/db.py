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
    ScrapedData,
    ScrapedDataCreate,
)
from app.fixtures.scraped_data import load_scraped_data


def get_url():
    user = os.getenv("PGUSER", "kubix")
    password = os.getenv("PGPASSWORD", "")
    server = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    db = os.getenv("PGDATABASE", "postgres")
    return f"postgresql+psycopg://{user}:{password}@{server}:{port}/{db}"


engine = create_engine(get_url())


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-template/issues/28


def fixtures(session: Session) -> None:
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

    scraped_data, countries, states, business_types = load_scraped_data()

    country_objs = session.exec(select(Country)).all()
    state_objs = session.exec(select(Location)).all()
    business_type_objs = session.exec(select(BusinessType)).all()
    scraped_data_objs = session.exec(select(ScrapedData)).all()

    if not country_objs:
        for country in countries:
            country_in = CountryCreate(name=country)
            db_obj = Country.model_validate(country_in)
            session.add(db_obj)

    if not state_objs:
        for state in states:
            state_in = LocationCreate(name=state)
            db_obj = Location.model_validate(state_in)
            session.add(db_obj)

    if not business_type_objs:
        for business_type in business_types:
            business_type_in = BusinessTypeCreate(name=business_type)
            db_obj = BusinessType.model_validate(business_type_in)
            session.add(db_obj)

    if not scraped_data_objs:
        for scraped_data in scraped_data:
            country = session.exec(
                select(Country).where(Country.name == scraped_data.country)
            ).first()
            location = session.exec(
                select(Location).where(Location.name == scraped_data.location)
            ).first()

            scraped_data_in = ScrapedDataCreate(
                company_name=scraped_data.title,
                business_type=scraped_data.business_type,
                company_address=scraped_data.address,
                company_phone=scraped_data.phone,
                country_id=country.id,
                location_id=location.id,
                state=scraped_data.location,
                zip_code=scraped_data.zip_code,
            )
            db_obj = ScrapedData.model_validate(scraped_data_in)
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
