from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, Response

from app.api.deps import CurrentUser, ScrapperAuthTokenDep, SessionDep
from app.core.logs import get_logger
from app.models import (
    ReservedCredit,
    ScraperEventData,
    ScrapingDataRequest,
    User,
)
from app.workflows.credits import release_credit, reserve_credit, use_credit
from app.workflows.scraper import (
    send_start_scraper_command,
    update_scraper_data_event_from_redis,
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

    # Check if the user has available credits or free access left
    if current_user.available_credit < 1:
        raise HTTPException(
            status_code=400,
            detail="You have already used your free access this month. Please purchase credits to access more leads.",
        )

    available_limit = current_user.available_credit

    # Ensure the limit does not exceed the available limit
    data.limit = min(data.limit, available_limit)

    if data.limit < 1:
        raise HTTPException(
            status_code=400,
            detail="You have no available credits.",
        )

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

    start_task = send_start_scraper_command(session, current_user, data)

    if not start_task["status"]:
        return JSONResponse(
            content={"detail": "Failed to start the scraper"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    reserve_credit(session, current_user, data.limit, start_task["task_id"])

    return JSONResponse(
        {"event_id": start_task["internal_id"]}, status_code=status.HTTP_200_OK
    )


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
    event = update_scraper_data_event_from_redis(session, event_id)
    if "status" in event and event["status"] == 404:
        return JSONResponse(
            {"detail": f"Scraper event with id {event_id} not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return event


@router.post(
    "/finish-notification/{task_id}", responses={200: {"description": "OK"}}
)
def finish_notification(
    session: SessionDep,
    has_access: ScrapperAuthTokenDep,
    task_id: str,
):
    """
    [Internal Only] Finish notification, should be hidden from the public API later
    """
    logger.info(
        "Scraper finished, reserved credits will be released - function finish_notification"
    )

    reserved_credit = (
        session.query(ReservedCredit).filter_by(task_id=task_id).first()
    )

    credits_to_use = reserved_credit.credits_reserved
    credits_remaining = credits_to_use

    user = session.get(User, reserved_credit.user_id)

    if user.free_credit > 0:
        credits_used_from_free = min(credits_to_use, user.free_credit)
        credits_remaining -= credits_used_from_free
        user.free_credit -= credits_used_from_free

    release_credit(session, reserved_credit, credits_remaining)

    session.commit()

    return Response(status_code=status.HTTP_200_OK)
