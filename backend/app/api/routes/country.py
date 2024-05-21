from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Country, CountryCreate, CountryBase, CountryPublic, CountriesPublic

router = APIRouter()


@router.get("/", response_model=CountriesPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Retrieve items.
    """

    count_statement = select(func.count()).select_from(Country)
    count = session.exec(count_statement).one()

    statement = select(Country)
    countries = session.exec(statement).all()

    return CountriesPublic(data=countries, count=count)