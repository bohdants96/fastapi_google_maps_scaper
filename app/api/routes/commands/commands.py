from fastapi import APIRouter, status
from fastapi.responses import Response

from app.api.deps import SessionDep, CurrentUser
from app.core.logs import get_logger
from app.models import (
    ScrapingDataRequest,
    ScraperEventData,
)

from app.workflows.scraper import (
    send_start_scraper_command,
    _update_scraper_data_event_from_redis,
)

router = APIRouter()

logger = get_logger()


@router.post("/start-scraper", responses={200: {"description": "OK"}})
def start_scraper(
    data: ScrapingDataRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> Response:
    """
    [Internal Only] Start scaper, should be hidden from the public API later
    """
    logger.info("Starting scrapper - function start_scraper")

    if not data.businesses:
        return Response(
            content={"detail": "At least one business is required"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not data.cities and not data.states:
        return Response(
            content={"detail": "At least one city or state is required"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not send_start_scraper_command(session, current_user, data):
        return Response(
            content={"detail": "Failed to start the scraper"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return Response(status_code=status.HTTP_200_OK)


@router.get("/get-scraper-status", response_model=ScraperEventData)
def get_scraper_status(
    session: SessionDep,
    current_user: CurrentUser,
    event_id: int,
):
    """
    [Internal Only] Get scaper status, should be hidden from the public API later
    """
    logger.info("Getting scrapper status - function get_scraper_status")
    event = _update_scraper_data_event_from_redis(session, event_id)
    return event
