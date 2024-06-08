from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.api.write_to_csv import write_to_csv
from app.core.logs import get_logger
from app.models import (
    BusinessLead,
    BusinessLeadAccessLog,
    BusinessLeadAccessLogCreate,
    BusinessLeadPublic,
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


@router.get("/", response_model=list[BusinessLeadPublic])
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

    if credits_to_use > 0:
        use_credit(session, current_user.id, credits_to_use)

    created_access_log = BusinessLeadAccessLogCreate(
        user_id=current_user.id,
        business_leads_ids={
            "business_leads_ids": [
                business_lead.id for business_lead in business_leads
            ]
        },
        credits_used=credits_to_use,
    )

    # Save the access log
    db_access_log = BusinessLeadAccessLog.model_validate(created_access_log)
    session.add(db_access_log)
    session.commit()
    logger.info(f"Found {len(business_leads)} business leads")
    return business_leads


@router.get("/download-csv")
def download_csv(
    session: SessionDep,
    current_user: CurrentUser,
    businesses: list[str] = Query(
        None, description="List of business types to filter"
    ),
    cities: list[str] = Query(None, description="List of cities to filter"),
    states: list[str] = Query(None, description="List of country to filter"),
    limit: int | None = None,
) -> Any:
    """
    Retrieve business leads and send it as a CSV file.
    """

    logger.info(
        "Retrieving business leads and send it as a CSV file - function download_csv."
    )
    statement = select(BusinessLead)

    if not businesses or not (cities or states):
        logger.error("Businesses and cities or states parameters is required.")
        raise HTTPException(
            status_code=400,
            detail="Businesses and cities or states parameters is required.",
        )

    if businesses:
        statement = statement.where(BusinessLead.business_type.in_(businesses))
    if states:
        statement = statement.where(BusinessLead.state.in_(states))
    if cities:
        statement = statement.where(BusinessLead.city.in_(cities))

    statement = statement.order_by(BusinessLead.received_date.desc())
    if limit:
        statement = statement.limit(limit)

    logger.info("statement: %s", statement)
    business_leads = session.exec(statement).all()

    csv_file_path = "business_lead.csv"
    logger.info(f"Found {len(business_leads)} business leads")

    write_to_csv(csv_file_path, headers, business_leads)
    logger.info(
        f"{len(business_leads)} business leads were written to {csv_file_path}"
    )

    return FileResponse(
        csv_file_path, media_type="text/csv", filename=csv_file_path
    )
