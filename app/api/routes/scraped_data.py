import csv
from io import StringIO
from typing import Any, List

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from sqlmodel import and_, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import ScrapedData, ScrapedDatasPublic

router = APIRouter()


@router.get("/", response_model=ScrapedDatasPublic)
def read_scraped_datas(
    session: SessionDep,
    current_user: CurrentUser,
    businesses: List[str] | None = Query(
        ..., description="List of business types to filter"
    ),
    countries: List[int] | None = Query(
        None, description="List of country ids to filter"
    ),
    locations: List[int] | None = Query(
        None, description="List of location ids to filter"
    ),
    limit: int = 30,
) -> Any:
    """
    Retrieve scraped data.
    """

    count_statement = select(func.count()).select_from(ScrapedData)
    count = session.exec(count_statement).one()

    statement = select(ScrapedData).limit(30)

    if businesses:
        statement = statement.where(ScrapedData.business_type.in_(businesses))

    if countries:
        statement = statement.where(ScrapedData.country_id.in_(countries))

    if locations:
        statement = statement.where(ScrapedData.location_id.in_(locations))

    statement = statement.limit(limit)
    scraped_datas = session.exec(statement).all()

    return ScrapedDatasPublic(data=scraped_datas, count=count)


@router.get("/download-csv")
def download_csv(
    session: SessionDep,
    current_user: CurrentUser,
    businesses: List[str] = Query(
        ..., description="List of business types to filter"
    ),
    countries: List[int] = Query(
        ..., description="List of country ids to filter"
    ),
    locations: List[int] | None = Query(
        None, description="List of location ids to filter"
    ),
    limit: int | None = None,
) -> Any:
    """
    Retrieve scraped data and send it as a CSV file.
    """

    statement = select(ScrapedData)

    filters = []
    if businesses:
        filters.append(ScrapedData.business_type.in_(businesses))
    if countries:
        filters.append(ScrapedData.country_id.in_(countries))
    if locations:
        filters.append(ScrapedData.location_id.in_(locations))

    statement = statement.where(and_(*filters))

    if limit:
        statement = statement.limit(limit)

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

    return FileResponse(
        csv_file_path, media_type="text/csv", filename=csv_file_path
    )
