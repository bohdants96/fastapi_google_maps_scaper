import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import Transaction, WebhookEvent

router = APIRouter()

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/one-time-payment")
async def one_time_payment(
    current_user: CurrentUser,
    credits: int,
    amount: float,
    currency: str,
    session: SessionDep,
):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency,
            metadata={"user_id": current_user.id, "credits": credits},
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    transaction = Transaction(
        user_id=current_user.id,
        stripe_payment_id=intent.id,
        amount=amount,
        currency=currency,
        status=intent.status,
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return {
        "client_secret": intent.client_secret,
        "transaction_id": transaction.id,
        "transaction_status": transaction.status,
    }


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, session: SessionDep):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        transaction = session.exec(
            select(Transaction).where(
                Transaction.stripe_payment_id == payment_intent["id"]
            )
        ).first()
        if transaction:
            transaction.status = "succeeded"
            session.add(transaction)
            session.commit()

    webhook_event = WebhookEvent(
        event_id=event.id, event_type=event.type, data=event.data
    )
    session.add(webhook_event)
    session.commit()

    return {"status": "success"}
