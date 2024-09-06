import datetime
import logging

from sqlmodel import Session, select

from app.core.logs import get_logger
from app.models import (
    BusinessLead,
    BusinessLeadInternal,
    BusinessOwnerInfo,
    BusinessOwnerInfoCreate,
    Education,
    House,
    PeopleLead,
    PeopleLeadInternal,
    Work,
)

logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

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
        scraped_record["received_date"] = datetime.datetime.now()
        employee = scraped_record.pop("employee")
        statement = select(BusinessLead).where(
            BusinessLead.company_phone == data.company_phone
        )
        db_data = session.exec(statement).first()

        db_data_employee = None

        if db_data:
            db_data.sqlmodel_update(scraped_record)
            session.add(db_data)
        else:
            db_obj = BusinessLead.model_validate(scraped_record)
            session.add(db_obj)
            session.flush()

        if employee:
            if db_data:
                employee["business_lead_id"] = db_data.id
            else:
                employee["business_lead_id"] = db_obj.id
            db_obj_employee = BusinessOwnerInfo.model_validate(employee)
            session.add(db_obj_employee)

    session.commit()
    logger.info("Scraped data processing completed")


def process_people_data(
    scraped_data: list[PeopleLeadInternal], session: Session
) -> None:
    # Process & save scraped data
    # check if phone number already exists
    # if exists, update the record
    # else create a new record

    logger.info(f"Processing scraped data [{len(scraped_data)} records]")

    for data in scraped_data:

        scraped_record = data.model_dump(exclude_unset=True)
        scraped_record["scraped_date"] = datetime.datetime.now()
        scraped_record["received_date"] = datetime.datetime.now()
        house = scraped_record.pop("house")
        works = scraped_record.pop("work")
        education = scraped_record.pop("education")

        if house:
            db_obj_house = House.model_validate(house)
            session.add(db_obj_house)
            session.flush()

        if education:
            db_obj_ed = Education.model_validate(education)
            session.add(db_obj_ed)
            session.flush()

        works_id = []
        if works:
            for work in works:
                db_obj_work = Work.model_validate(work)
                session.add(db_obj_work)
                session.flush()
                works_id.append(db_obj_work.id)

        if scraped_record:
            scraped_record["education_id"] = db_obj_ed.id
            scraped_record["house_id"] = db_obj_house.id
            scraped_record["works_id"] = works_id
            db_obj = PeopleLead.model_validate(scraped_record)
            session.add(db_obj)

    session.commit()
    logger.info("Scraped data processing completed")
