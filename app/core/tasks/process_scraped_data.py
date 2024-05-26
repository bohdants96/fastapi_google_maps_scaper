import logging

from app.models import ScrapedData, ScrapedDataInternal
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


def process_scraped_data(
    scraped_data: list[ScrapedDataInternal], session: Session
) -> None:
    # Process & save scraped data
    # check if phone number already exists
    # if exists, update the record
    # else create a new record

    logger.info(f"Processing scraped data [{len(scraped_data)} records]")

    for data in scraped_data:
        if not data.company_phone:
            logger.warning("Skipping record: company_phone is missing")
            continue

        scraped_record = data.model_dump(exclude_unset=True)
        statement = select(ScrapedData).where(
            ScrapedData.company_phone == data.company_phone
        )
        db_data = session.exec(statement).first()

        if db_data:
            db_data.sqlmodel_update(scraped_record)
            session.add(db_data)
        else:
            db_obj = ScrapedData.model_validate(scraped_record)
            session.add(db_obj)

    session.commit()
    logger.info("Scraped data processing completed")
