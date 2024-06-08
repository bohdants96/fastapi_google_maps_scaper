import requests
import redis
import json

from sqlmodel import Session

from app.models import (
    User,
    ScrapingDataRequest,
    ScraperEventData,
    ScraperEventCreate,
    ScraperEventUpdate,
)
from app.core.config import settings

from app.core.logs import get_logger

logger = get_logger()


redis_db = redis.from_url(settings.REDIS_URI, decode_responses=True)


def _update_scraper_data_event_from_redis(
    session: Session, event_id: int
) -> ScraperEventData:
    event_data = redis_db.get(f"scraper_event_{event_id}")
    if not event_data:
        raise ValueError(f"Scraper event with id {event_id} not found")

    event_data = json.loads(event_data)
    event = _get_scraper_data_event(session, event_id)
    _update_scraper_data_event(
        session, event, ScraperEventUpdate(**event_data)
    )
    return event


def _get_scraper_data_event(
    session: Session, event_id: int
) -> ScraperEventData:
    scraper_event = session.get(ScraperEventData, event_id)
    if not scraper_event:
        raise ValueError(f"Scraper event with id {event_id} not found")
    return scraper_event


def _create_scraper_data_event(session: Session, data: ScraperEventCreate):
    db_obj = ScraperEventData.model_validate(data)
    session.add(db_obj)
    session.commit()


def _update_scraper_data_event(
    session: Session, scraper_event: ScraperEventData, data: ScraperEventUpdate
):
    event_data = data.model_dump(exclude_unset=True)
    scraper_event.sqlmodel_update(event_data)
    session.add(scraper_event)
    session.commit()
    session.refresh(scraper_event)


def send_start_scraper_command(
    session: Session, user: User, data: ScrapingDataRequest
) -> bool:

    scraper_event = _create_scraper_data_event(
        session, ScraperEventCreate(user_id=user.id, status="started")
    )
    data.sqlmodel_update({"task_id": scraper_event.id})

    request_url = f"{settings.INTERNAL_SCRAPER_API_ADDRESS}/start-scraper?token=supersecrettoken"
    response = requests.post(request_url, json=data.model_dump_json())

    if response.status_code != 200:
        logger.error(
            f"Failed to start the scraper. Status code: {response.status_code}. Response: {response.text}"
        )
        return False

    task_id = response.json().get("task_id")
    if not task_id:
        logger.error(
            f"Failed to start the scraper. Task ID not found in response"
        )
        return False

    _update_scraper_data_event(
        session,
        scraper_event,
        ScraperEventUpdate(
            task_id=task_id,
            status="running",
            total_results=0,
            scraped_results=0,
        ),
    )
    return True
