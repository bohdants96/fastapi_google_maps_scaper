from fastapi import APIRouter, responses, status

from app.api.deps import SessionDep
from app.core.logs import get_logger
from app.core.tasks.send_support_email import send_to_support
from app.models import Ticket, TicketRequest

router = APIRouter()

logger = get_logger()


@router.post("/create-ticket")
def create_ticket(
    session: SessionDep, data: TicketRequest
) -> responses.Response:

    logger.info("Starting function create_ticket")

    data = data.model_dump(exclude_unset=True)
    db_obj = Ticket.model_validate(data)

    try:
        session.add(db_obj)
        session.commit()
        send_to_support(db_obj)
    except Exception as e:
        logger.error(e)
        return responses.JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)}
        )

    logger.info("Successful create_ticket!")
    return responses.Response(status_code=status.HTTP_202_ACCEPTED)
