import csv
from io import StringIO
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from sqlmodel import and_, select

from app.api.deps import CurrentUser, SessionDep
from app.models import ScrapedData, ScrapedDataPublic

router = APIRouter()


@router.get("/", response_model=list[ScrapedDataPublic])
def read_scraped_datas(
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
    Retrieve scraped data.
    """
    statement = select(ScrapedData)

    if not businesses or not (cities or states):
        raise HTTPException(
            status_code=400,
            detail="Businesses and cities or states parameters is required.",
        )

    if businesses:
        statement = statement.where(ScrapedData.business_type.in_(businesses))
    if states:
        statement = statement.where(ScrapedData.state.in_(states))
    if cities:
        statement = statement.where(ScrapedData.city.in_(cities))

    statement = statement.limit(limit)
    scraped_datas = session.exec(statement).all()
    return scraped_datas


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
    Retrieve scraped data and send it as a CSV file.
    """

    statement = select(ScrapedData)

    if not businesses or not (cities or states):
        raise HTTPException(
            status_code=400,
            detail="Businesses and cities or states parameters is required.",
        )

    if businesses:
        statement = statement.where(ScrapedData.business_type.in_(businesses))
    if states:
        statement = statement.where(ScrapedData.state.in_(states))
    if cities:
        statement = statement.where(ScrapedData.city.in_(cities))

    statement = statement.order_by(ScrapedData.received_date.desc())
    if limit:
        statement = statement.limit(limit)

    print("statement: %s", statement)
    scraped_datas = session.exec(statement).all()

    csv_file_path = "scraped_data.csv"

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "id",
            "company name",
            "company address",
            "company phone",
            "website",
            "country",
            "city",
            "state",
            "couty",
            "zip code",
        ]
    )

    for data in scraped_datas:
        writer.writerow(
            [
                data.id,
                data.company_name,
                data.company_address,
                data.company_phone,
                data.website,
                data.country,
                data.city,
                data.state,
                data.county,
                data.zip_code,
            ]
        )

    with open(csv_file_path, "w", newline="") as file:
        file.write(output.getvalue())

    return FileResponse(
        csv_file_path, media_type="text/csv", filename=csv_file_path
    )
