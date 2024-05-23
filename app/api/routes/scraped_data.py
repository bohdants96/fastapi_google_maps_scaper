from typing import Any, List

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from sqlmodel import func, select, and_

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ScrapedData,
    ScrapedDatasPublic,
    Location,
    Country,
)

import csv
from io import StringIO

router = APIRouter()


@router.get("/", response_model=ScrapedDatasPublic)
def read_scraped_datas(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Retrieve scraped data.
    """

    count_statement = select(func.count()).select_from(ScrapedData)
    count = session.exec(count_statement).one()

    statement = select(ScrapedData)
    scraped_datas = session.exec(statement).all()

    return ScrapedDatasPublic(data=scraped_datas, count=count)


@router.get("/download-csv")
def download_csv(
    session: SessionDep,
    current_user: CurrentUser,
    businesses: List[str] = Query(..., description="List of business types to filter"),
    countries: List[str] = Query(..., description="List of countries to filter"),
    cities: List[str] = Query(None, description="List of cities to filter"),
    amount: int = None,
) -> Any:
    """
    Retrieve scraped data and send it as a CSV file.
    """

    statement = select(ScrapedData)

    filters = []
    if businesses:
        filters.append(ScrapedData.business_type.in_(businesses))
    if countries:
        countries_ids_subquery = select(Country.id).where(Country.name.in_(countries))
        filters.append(ScrapedData.country_id.in_(countries_ids_subquery))
    if cities:
        location_ids_subquery = select(Location.id).where(Location.name.in_(cities))
        filters.append(ScrapedData.location_id.in_(location_ids_subquery))

    statement = statement.where(and_(*filters)).limit(amount)
    scraped_datas = session.exec(statement).all()

    csv_file_path = "scraped_data.csv"

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "id",
            "company_name",
            "business_type",
            "company_address",
            "company_phone",
            "country_id",
            "location_id",
            "state",
            "zip_code",
            "created_at",
        ]
    )

    for data in scraped_datas:
        writer.writerow(
            [
                data.id,
                data.company_name,
                data.business_type,
                data.company_address,
                data.company_phone,
                data.country_id,
                data.location_id,
                data.state,
                data.zip_code,
                data.created_at,
            ]
        )

    with open(csv_file_path, "w", newline="") as file:
        file.write(output.getvalue())

    return FileResponse(csv_file_path, media_type="text/csv", filename=csv_file_path)
