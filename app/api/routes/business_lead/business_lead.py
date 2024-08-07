import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.api.write_to_csv import write_to_csv
from app.core.logs import get_logger
from app.models import (
    BusinessLead,
    BusinessLeadPublic,
    SearchHistory,
    SearchHistoryCreate,
)
from app.workflows.credits import use_credit

router = APIRouter()

logger = get_logger()

headers = [
    "company_name",
    "company_address",
    "company_phone",
    "website",
    "business_type",
]


@router.get(
    "/",
    response_model=list[BusinessLeadPublic],
    description="Retrieve business leads. Must have cities or states and list of business types to filter",
)
def read_business_lead(
    session: SessionDep,
    current_user: CurrentUser,
    businesses: list[str] = Query(
        None, description="List of business types to filter"
    ),
    cities: list[str] = Query(None, description="List of cities to filter"),
    states: list[str] = Query(None, description="List of country to filter"),
    limit: int = 30,
) -> Any:
    """
    Retrieve business leads.
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

    logger.info("Retrieving business leads - function read_business_lead.")
    statement = select(BusinessLead)

    # Validate input parameters
    if not businesses or not (cities or states):
        logger.error(
            "Businesses and cities or states parameters are required."
        )
        raise HTTPException(
            status_code=400,
            detail="Businesses and cities or states parameters are required.",
        )

    # Apply filters based on the input parameters
    if businesses:
        statement = statement.where(BusinessLead.business_type.in_(businesses))
    if states:
        statement = statement.where(BusinessLead.state.in_(states))
    if cities:
        statement = statement.where(BusinessLead.city.in_(cities))

    # Limit the results to the requested limit
    statement = statement.limit(limit)
    business_leads = session.exec(statement).all()

    # If no free access left and user has available credits, use credits
    credits_to_use = min(limit, len(business_leads))
    credits_remaining = credits_to_use

    created_access_log = SearchHistoryCreate(
        user_id=current_user.id,
        internal_search_ids={
            "internal_search_ids": [business_lead.id for business_lead in business_leads]  # type: ignore
        },
        credits_used=credits_to_use,
        source="business",
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
    logger.info(f"Found {len(business_leads)} business leads")
    return business_leads


@router.get(
    "/download-csv",
    description="Retrieve business leads and send it as a CSV file.",
)
def download_csv(
    session: SessionDep,
    current_user: CurrentUser,
    search_history_id: int,
) -> Any:
    """
    Retrieve business leads and send it as a CSV file.
    """

    logger.info(
        "Retrieving business leads and send it as a CSV file - function download_csv."
    )
    statement = select(SearchHistory).where(
        SearchHistory.user_id == current_user.id,
        SearchHistory.id == search_history_id,
    )
    search_history = session.exec(statement).first()
    if not search_history:
        return JSONResponse(
            {"message": "No search history found."}, status_code=404
        )

    internal_searches = []
    for internal_search_id in search_history.internal_search_ids[
        "internal_search_ids"
    ]:
        statement = select(BusinessLead).where(
            BusinessLead.id == internal_search_id,
        )
        internal_search = session.exec(statement).first()
        if internal_search:
            internal_searches.append(internal_search)

    csv_file_path = "business_lead.csv"
    logger.info(f"Found {len(internal_searches)} business leads")

    write_to_csv(csv_file_path, headers, internal_searches)
    logger.info(
        f"{len(internal_searches)} business leads were written to {csv_file_path}"
    )

    return FileResponse(
        csv_file_path, media_type="text/csv", filename=csv_file_path
    )


@router.get(
    "/download-csv-admin",
    description="Retrieve business leads and send it as a CSV file for superuser.",
    include_in_schema=False,
)
def download_csv_admin(
    session: SessionDep,
    current_user: CurrentUser,
    businesses: list[str] = Query(
        None, description="List of business types to filter"
    ),
    received_date: datetime.datetime = Query(
        None, description="Filter business leads by received date"
    ),
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this resource.",
        )

    logger.info(
        "Retrieving business leads and send it as a CSV file - function download_csv_admin."
    )
    statement = select(BusinessLead)
    if businesses:
        statement = statement.where(BusinessLead.business_type.in_(businesses))

    if received_date:
        statement = statement.where(
            BusinessLead.received_date >= received_date
        )

    statement = statement.order_by(BusinessLead.received_date.desc())
    business_leads = session.exec(statement).all()
    csv_file_path = "business_leads.csv"
    logger.info(f"Found {len(business_leads)} business leads")

    write_to_csv(csv_file_path, headers, business_leads)

    return FileResponse(
        csv_file_path, media_type="text/csv", filename=csv_file_path
    )
