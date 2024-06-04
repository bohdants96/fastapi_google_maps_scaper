from sqlmodel import Session, select

from app.core.logs.logs import get_logger
from app.models import BusinessLead, BusinessLeadInternal

logger = get_logger()


def process_scraped_data(
    scraped_data: list[BusinessLeadInternal], session: Session
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
        statement = select(BusinessLead).where(
            BusinessLead.company_phone == data.company_phone
        )
        db_data = session.exec(statement).first()

        if db_data:
            db_data.sqlmodel_update(scraped_record)
            session.add(db_data)
        else:
            db_obj = BusinessLead.model_validate(scraped_record)
            session.add(db_obj)

    session.commit()
    logger.info("Scraped data processing completed")
