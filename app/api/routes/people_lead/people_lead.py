import datetime
import logging
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.core.logs import get_logger
from app.models import (
    PeopleDataRequest,
    PeopleLead,
    PeopleLeadPublic,
    SearchHistory,
    SearchHistoryCreate,
)
from app.workflows.credits import use_credit

router = APIRouter()

logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logger = get_logger()


@router.post(
    "/",
    response_model=list[PeopleLeadPublic],
    description="Retrieve people leads. Must have cities or states to filter",
)
def read_people_lead(
    session: SessionDep,
    current_user: CurrentUser,
    data: list[PeopleDataRequest] | None = Body(None),
    limit: int = 30,
) -> Any:
    """
    Retrieve people leads.
    """

    # Check if the user has available credits or free access left
    if current_user.available_credit < 1:
        raise HTTPException(
            status_code=400,
            detail="You have already used your free access this month. Please purchase credits to access more leads.",
        )

    available_limit = current_user.available_credit

    # Ensure the limit does not exceed the available limit
    limit = min(limit, available_limit)

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="You have no available credits.",
        )

    logger.info("Retrieving people leads - function read_people_lead.")
    people_leads = []

    # Validate input parameters
    if len(data) <= 0:
        logger.error("Cities, states and streets parameters are required.")
        raise HTTPException(
            status_code=400,
            detail="Cities or states parameters are required.",
        )

    for item in data:
        if not item.city or not item.streets:
            logger.error("Cities and states parameters are required.")
            raise HTTPException(
                status_code=400,
                detail="Cities or states parameters are required.",
            )

        if not item.streets or len(item.streets) == 0:
            statement = select(PeopleLead).where(
                PeopleLead.city == item.city,
                PeopleLead.state == item.state,
            )
        else:
            statement = select(PeopleLead).where(
                PeopleLead.city == item.city,
                PeopleLead.state == item.state,
                PeopleLead.street.in_(item.streets),
            )

        # Limit the results to the requested limit
        statement = statement.limit(limit)
        people_lead = session.exec(statement).all()
        people_leads.extend(people_lead)

    # If no free access left and user has available credits, use credits
    credits_to_use = min(limit, len(people_leads))
    credits_remaining = credits_to_use

    created_access_log = SearchHistoryCreate(
        user_id=current_user.id,
        internal_search_ids={
            "internal_search_ids": [people_lead.id for people_lead in people_leads]  # type: ignore
        },
        credits_used=credits_to_use,
        source="people",
        status="Finished",
        search_time=datetime.datetime.now(),
    )

    db_access_log = SearchHistory.model_validate(created_access_log)
    session.add(db_access_log)
    session.commit()

    if current_user.free_credit > 0:
        credits_used_from_free = min(credits_to_use, current_user.free_credit)
        credits_remaining -= credits_used_from_free
        current_user.free_credit -= credits_used_from_free

    if credits_remaining > 0:
        use_credit(session, current_user.id, credits_remaining)

    session.commit()
    logger.info(f"Found {len(people_leads)} people leads")
    return people_leads
