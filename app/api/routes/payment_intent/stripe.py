from typing import Annotated

import stripe
from fastapi import APIRouter, Body, HTTPException, Request

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.logs import get_logger
from app.models import CreatePaymentIntent, TransactionCreate, WebhookEvent
from app.workflows.transactions import create_transaction
from app.workflows.webhooks import handle_payment_intent_succeeded

router = APIRouter()

logger = get_logger()

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@router.post(
    "/create-payment-intent",
    description="This endpoint creates one time payments to get credits.",
)
async def payment_intent(
    current_user: CurrentUser,
    session: SessionDep,
    create_payment_intent: Annotated[
        CreatePaymentIntent,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** payment works correctly.",
                    "value": {
                        "credits": 10,
                        "amount": 10,
                    },
                },
            },
        ),
    ],
):
    logger.info("Create one time payment - function one_time_payment")
    try:
        logger.info("Try to create one time payment with stripe")
        intent = stripe.PaymentIntent.create(
            amount=int(create_payment_intent.amount * 100),
            currency="USD",
            metadata={
                "user_id": str(current_user.id),
                "credits": str(create_payment_intent.credits),
            },
            automatic_payment_methods={"enabled": True},
        )
    except stripe.error.StripeError as e:  # type: ignore
        logger.error(e)
        raise HTTPException(status_code=400, detail=str(e))

    transaction = create_transaction(
        session,
        TransactionCreate(
            stripe_payment_id=intent.id,
            user_id=current_user.id,  # type: ignore
            amount=create_payment_intent.amount,
            status="pending",
            currency="USD",
        ),
    )

    logger.info("Create one time payment with stripe")
    return {
        "client_secret": intent.client_secret,
        "transaction_id": transaction.id,
        "transaction_status": transaction.status,
    }


@router.post(
    "/webhook",
    description="This is webhook endpoint, which change payment status when it will finish.",
)
async def webhook_handler(request: Request, session: SessionDep):
    logger.info("Call stripe-webhook")
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    logger.info("Trying construct event for Webhook")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        logger.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:  # type: ignore
        logger.error("Signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event_type := event.get("type"):
        if event_type == "payment_intent.succeeded":
            handle_payment_intent_succeeded(session, event)
        else:
            logger.info("Event type not supported")
            return {"status": "success"}

    webhook_event = WebhookEvent(
        event_id=event.id, event_type=event.type, data=event.data
    )
    session.add(webhook_event)
    session.commit()

    logger.info("Webhook event received")
    return {"status": "success"}
