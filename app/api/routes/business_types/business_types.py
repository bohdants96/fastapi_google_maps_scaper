from fastapi import APIRouter
from sqlmodel import select

from app.models import PublicBusinessType, BusinessType
from app.api.deps import CurrentUser, SessionDep

from fastapi_pagination import LimitOffsetPage, paginate


router = APIRouter()


@router.get("/", response_model=LimitOffsetPage[PublicBusinessType])
def read_business_types(
    session: SessionDep, current_user: CurrentUser
) -> LimitOffsetPage[PublicBusinessType]:
    statement = select(BusinessType).order_by(BusinessType.name)
    business_types = session.exec(statement).all()
    return paginate(business_types)
