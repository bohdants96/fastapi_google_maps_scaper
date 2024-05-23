from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Location, LocationCreate, LocationBase, LocationPublic, LocationsPublic

router = APIRouter()


@router.get("/", response_model=LocationsPublic)
def read_locations(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Retrieve locations.
    """

    count_statement = select(func.count()).select_from(Location)
    count = session.exec(count_statement).one()

    statement = select(Location)
    locations = session.exec(statement).all()

    return LocationsPublic(data=locations, count=count)