import json
from typing import Dict

import redis
import requests
from sqlmodel import Session

from app.core.config import settings
from app.core.logs import get_logger
from app.models import (
    InternalScrapingDataRequest,
    ScraperEventCreate,
    ScraperEventData,
    ScraperEventUpdate,
    ScrapingDataRequest,
    User,
)

logger = get_logger()

redis_db = redis.from_url(settings.REDIS_URI, decode_responses=True)


def update_scraper_data_event_from_redis(
    session: Session, event_id: int
) -> dict[str, int] | ScraperEventData:
    event_data = redis_db.get(f"scraping_event_{event_id}")
    if not event_data:
        return {"status": 404}

    event_data = json.loads(event_data)
    event = _get_scraper_data_event(session, event_id)
    if event is None:
        return {"status": 404}
    event_data["task_id"] = event.task_id
    event_data["status"] = event.status
    _update_scraper_data_event(
        session, event, ScraperEventUpdate(**event_data)
    )
    return event


def _get_scraper_data_event(
    session: Session, event_id: int
) -> ScraperEventData:
    scraper_event = session.get(ScraperEventData, event_id)
    return scraper_event


def _create_scraper_data_event(session: Session, data: ScraperEventCreate):
    db_obj = ScraperEventData.model_validate(data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


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
) -> dict:
    scraper_event = _create_scraper_data_event(
        session, ScraperEventCreate(user_id=user.id, status="started")
    )

    redis_key = f"scraping_event_{scraper_event.id}"
    redis_db.set(
        redis_key,
        json.dumps(
            {
                "scraped_results": 0,
                "total_results": 0,
            }
        ),
    )

    data = InternalScrapingDataRequest(
        internal_id=scraper_event.id,
        businesses=data.businesses,
        cities=data.cities,
        states=data.states,
        limit=data.limit,
        email=data.email,
    )

    request_url = f"{settings.INTERNAL_SCRAPER_API_ADDRESS}/start-scraping?token=supersecrettoken"
    response = requests.post(request_url, json=data.model_dump())

    if response.status_code != 200:
        logger.error(
            f"Failed to start the scraper. Status code: {response.status_code}. Response: {response.text}"
        )
        return {"status": False}

    task_id = response.json().get("task_id")
    if not task_id:
        logger.error(
            f"Failed to start the scraper. Task ID not found in response"
        )
        return {"status": False}

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
    return {
        "status": True,
        "task_id": task_id,
        "internal_id": scraper_event.id,
    }
