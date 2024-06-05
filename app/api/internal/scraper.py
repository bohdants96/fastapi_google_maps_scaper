from fastapi import APIRouter, BackgroundTasks, responses, status

from app.api.deps import ScrapperAuthTokenDep, SessionDep
from app.core.logs.logs import get_logger
from app.core.tasks.process_scraped_data import process_scraped_data
from app.models import BusinessLeadInternal

router = APIRouter()

logger = get_logger()


@router.post(
    "/scraped-data",
    responses={
        "202": {"description": "Accepted"},
        "204": {"description": "No Content"},
        "401": {"description": "Unauthorized"},
        "422": {"description": "Unprocessable Entity"},
    },
)
def create_scraped_data(
    scraped_data: list[BusinessLeadInternal],
    session: SessionDep,
    has_access: ScrapperAuthTokenDep,
    background_tasks: BackgroundTasks,
) -> responses.Response:
    """
    [Internal Only] Pass scraped data to the background task for processing.
    """
    logger.info(
        "Pass business leads to the background task for processing - function create_scraped_data"
    )
    if not has_access:
        logger.error("Unauthorized")
        return responses.Response(status_code=status.HTTP_401_UNAUTHORIZED)

    if not scraped_data:
        logger.error("No Content")
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

    background_tasks.add_task(process_scraped_data, scraped_data, session)
    logger.info("Scraped")
    return responses.Response(status_code=status.HTTP_202_ACCEPTED)


@router.post(
    "/business-leads",
    responses={
        "202": {"description": "Accepted"},
        "204": {"description": "No Content"},
        "401": {"description": "Unauthorized"},
        "422": {"description": "Unprocessable Entity"},
    },
)
def create_business_leads(
    business_leads: list[BusinessLeadInternal],
    session: SessionDep,
    has_access: ScrapperAuthTokenDep,
    background_tasks: BackgroundTasks,
) -> responses.Response:
    """
    [Internal Only] Pass scraped data to the background task for processing.
    """
    logger.info(
        "Pass business leads to the background task for processing - function create_scraped_data"
    )
    if not has_access:
        logger.error("Unauthorized")
        return responses.Response(status_code=status.HTTP_401_UNAUTHORIZED)

    if not business_leads:
        logger.error("No Content")
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

    background_tasks.add_task(process_scraped_data, business_leads, session)
    logger.info("Scraped")
    return responses.Response(status_code=status.HTTP_202_ACCEPTED)


@router.post(
    "/start-scraper",
    responses={
        "202": {"description": "Accepted"},
        "204": {"description": "No Content"},
        "401": {"description": "Unauthorized"},
        "422": {"description": "Unprocessable Entity"},
    },
)
def start_scraper(
    scraped_data: list[BusinessLeadInternal],
    session: SessionDep,
    has_access: ScrapperAuthTokenDep,
    background_tasks: BackgroundTasks,
) -> responses.Response:
    """
    [Internal Only] Start scaper
    """
    logger.info("Starting scrapper - function start_scraper")
    if not has_access:
        logger.error("Unauthorized")
        return responses.Response(status_code=status.HTTP_401_UNAUTHORIZED)

    if not scraped_data:
        logger.error("No Content")
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

    return responses.Response(status_code=status.HTTP_200_OK)
