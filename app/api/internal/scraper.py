from fastapi import APIRouter, BackgroundTasks, responses, status

from app.api.deps import SessionDep, ScrapperAuthTokenDep
from app.models import ScrapedDataInternal
from app.core.tasks.process_scraped_data import process_scraped_data

router = APIRouter()


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
    scraped_data: list[ScrapedDataInternal],
    session: SessionDep,
    has_access: ScrapperAuthTokenDep,
    background_tasks: BackgroundTasks,
) -> responses.Response:
    """
    [Internal Only] Pass scraped data to the background task for processing.
    TODO: hide this endpoint later
    """
    if not has_access:
        return responses.Response(status_code=status.HTTP_401_UNAUTHORIZED)

    if not scraped_data:
        return responses.Response(status_code=status.HTTP_204_NO_CONTENT)

    background_tasks.add_task(process_scraped_data, scraped_data, session)
    return responses.Response(status_code=status.HTTP_202_ACCEPTED)
