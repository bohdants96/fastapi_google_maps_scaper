from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.api.write_to_csv import write_to_csv
from app.core.logs.logs import get_logger
from app.models import (
    BusinessLead,
    BusinessLeadPublic,
    BusinessLeadAccessLogCreate,
    BusinessLeadAccessLog,
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

    if (
        current_user.available_credit < 1
        and current_user.used_free_access_this_month
    ):
        return HTTPException(
            status_code=400,
            detail="You have already used your free access this month. Please purchase credits to access more leads.",
        )

    if not current_user.used_free_access_this_month:
        available_limit = (
            250 + current_user.available_credit
        ) - current_user.free_business_leads_left

    limit = min(limit, available_limit)

    logger.info("Retrieving business leads - function read_business_lead.")
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

    statement = statement.limit(limit)
    business_leads = session.exec(statement).all()

    if available_limit <= 0 and current_user.used_free_access_this_month:
        use_credit(session, current_user.id, len(business_leads))  # type: ignore

        created_access_log = BusinessLeadAccessLogCreate(
            user_id=current_user.id,  # type: ignore
            free_access=False,
            business_leads_ids={
                "business_leads_ids": [business_lead.id for business_lead in business_leads]  # type: ignore
            },
            credits_used=len(business_leads),
        )
    else:
        created_access_log = BusinessLeadAccessLogCreate(
            user_id=current_user.id,  # type: ignore
            free_access=True,
            business_leads_ids={
                "business_leads_ids": [business_lead.id for business_lead in business_leads]  # type: ignore
            },
            credits_used=0,
        )

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
