from fastapi import APIRouter
from fastapi_pagination import LimitOffsetPage, paginate
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Address, PublicAddress

router = APIRouter()


@router.get("/", response_model=LimitOffsetPage[PublicAddress])
def read_address(
    city: str, session: SessionDep, current_user: CurrentUser
) -> LimitOffsetPage[PublicAddress]:
    statement = (
        select(Address)
        .where(func.lower(Address.city).ilike(f"%{city.lower()}%"))
        .order_by(Address.city)
    )
    address = session.exec(statement).all()
    return paginate(address)
