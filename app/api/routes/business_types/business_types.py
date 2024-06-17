from fastapi import APIRouter
from fastapi_pagination import LimitOffsetPage, paginate
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import BusinessType, PublicBusinessType

router = APIRouter()


@router.get("/", response_model=LimitOffsetPage[PublicBusinessType])
def read_business_types(
    session: SessionDep, current_user: CurrentUser
) -> LimitOffsetPage[PublicBusinessType]:
    statement = select(BusinessType).order_by(BusinessType.name)
    business_types = session.exec(statement).all()
    return paginate(business_types)


@router.get("/", response_model=LimitOffsetPage[PublicBusinessType])
def read_business_type(
    name: str, session: SessionDep, current_user: CurrentUser
) -> LimitOffsetPage[PublicBusinessType]:
    statement = select(BusinessType).where(
        func.lower(BusinessType.name).ilike(f"%{name.lower()}%")
    )
    business_types = session.exec(statement).all()
    return paginate(business_types)
