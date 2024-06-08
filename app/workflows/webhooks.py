from stripe import Event

from app.core.logs import get_logger

from app.workflows.credits import get_credit
from app.workflows.transactions import (
    create_transaction,
    get_transaction_by_stripe_payment_id,
    update_transaction_status,
)

from app.models import TransactionCreate

from sqlmodel import Session

logger = get_logger()


def handle_payment_intent_succeeded(session: Session, event: Event):
    print("Payment intent succeeded")
    logger.info("Updating status")
    payment_intent = event["data"]["object"]
    transaction = get_transaction_by_stripe_payment_id(
        session, payment_intent["id"]
    )
    metadata = event["data"]["object"]["metadata"]
    _credits = int(metadata.get("credits", 0))
    user_id = int(metadata.get("user_id", 0))

    if not user_id or not _credits:
        raise ValueError("User id or credits not found in metadata")

    if transaction is None:
        print("Transaction is None, creating new one")
        transaction = create_transaction(
            session,
            TransactionCreate(
                stripe_payment_id=payment_intent["id"],
                user_id=user_id,
                amount=payment_intent["amount"],
                status="pending",
                currency="USD",
            ),
        )

    print("Updating transaction status")
    update_transaction_status(session, transaction, "succeeded")

    print("Getting credit")
    get_credit(session, user_id, _credits)
