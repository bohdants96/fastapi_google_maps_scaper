from app.models import Transaction, TransactionCreate
from sqlmodel import Session, select


def create_transaction(session: Session, transaction: TransactionCreate):
    db_transaction = Transaction.model_validate(transaction)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


def get_transaction(session: Session, transaction_id: int):
    return session.get(Transaction, transaction_id)


def get_transaction_by_stripe_payment_id(
    session: Session, stripe_payment_id: str
):
    return session.exec(
        select(Transaction).where(
            Transaction.stripe_payment_id == stripe_payment_id
        )
    ).first()


def update_transaction_status(
    session: Session, transaction: Transaction, status: str
):
    transaction.status = status
    session.commit()
    session.refresh(transaction)
    return transaction
