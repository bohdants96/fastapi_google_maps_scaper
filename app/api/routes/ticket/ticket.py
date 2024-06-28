from typing import Annotated

from fastapi import APIRouter, Body, responses, status

from app.api.deps import SessionDep
from app.core.logs import get_logger
from app.core.tasks.send_support_email import send_to_support
from app.models import Ticket, TicketRequest

router = APIRouter()

logger = get_logger()


@router.post(
    "/create-ticket",
    description="By this endpoint user can write a request to support team. Full name, email and message are required.",
)
def create_ticket(
    session: SessionDep,
    data: Annotated[
        TicketRequest,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** ticket works correctly.",
                    "value": {
                        "full_name": "Test User",
                        "subject": "My problem",
                        "company_name": "Company Name",
                        "mobile_phone": "+380999999999",
                        "email": "test@email.com",
                        "message": "Here is my problem.",
                    },
                },
                "wrong phone": {
                    "summary": "A wrong mobile phone",
                    "description": "Mobile phone must meet the standard.",
                    "value": {
                        "full_name": "Test User",
                        "subject": "My problem",
                        "company_name": "Company Name",
                        "mobile_phone": "09999999",
                        "email": "test@email.com",
                        "message": "Here is my problem.",
                    },
                },
                "wrong email": {
                    "summary": "A wrong email address",
                    "description": "Email must meet the standard.",
                    "value": {
                        "full_name": "Test User",
                        "subject": "My problem",
                        "company_name": "Company Name",
                        "mobile_phone": "+380999999999",
                        "email": "testemail.com",
                        "message": "Here is my problem.",
                    },
                },
                "without required value": {
                    "summary": "Without required value",
                    "description": "Full name, email and message are required.",
                    "value": {
                        "full_name": "Test User",
                        "subject": "My problem",
                        "company_name": "Company Name",
                        "mobile_phone": "+380999999999",
                        "email": "test@email.com",
                    },
                },
            }
        ),
    ],
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
