from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import BusinessType, BusinessTypeCreate, BusinessTypeBase, BusinessTypePublic, BusinessTypesPublic

router = APIRouter()


@router.get("/", response_model=BusinessTypesPublic)
def read_business_types(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Retrieve business types.
    """

    count_statement = select(func.count()).select_from(BusinessType)
    count = session.exec(count_statement).one()

    statement = select(BusinessType)
    business_types = session.exec(statement).all()

    return BusinessTypesPublic(data=business_types, count=count)