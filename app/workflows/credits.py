from sqlmodel import Session

from app.models import Credit, ReservedCredit, User


def create_credit(session: Session, user_id: int) -> Credit:
    credit = Credit(user_id=user_id, total_credit=0, used_credit=0)
    session.add(credit)
    session.commit()
    return credit


def get_credit(session: Session, user_id: int, amount: int) -> None:
    credit = session.get(Credit, user_id)
    if credit is None:
        credit = create_credit(session, user_id)

    credit.total_credit += amount
    session.commit()


def use_credit(session: Session, user_id: int, amount: int) -> None:
    credit = session.get(Credit, user_id)
    if credit is None:
        credit = create_credit(session, user_id)

    credit.used_credit += amount
    session.commit()


def create_reserved_credit(
    session: Session, user_id: int, amount: int, task_id: int
) -> ReservedCredit:
    reserved_credit = ReservedCredit(
        user_id=user_id,
        credits_reserved=amount,
        task_id=task_id,
        status="reserved",
    )
    session.add(reserved_credit)
    session.commit()
    return reserved_credit


def reserve_credit(
    session: Session, user: User, amount: int, task_id: int
) -> None:
    credit = session.get(Credit, user.id)
    if credit is None:
        raise ValueError("Insufficient credits. Create credit first.")

    if user.available_credit < amount:
        raise ValueError("Insufficient credits")

    create_reserved_credit(session, user.id, amount, task_id)  # type: ignore
    use_credit(session, user.id, amount)  # type: ignore
    session.commit()


def release_credit(session: Session, reserved_credit: ReservedCredit) -> None:
    reserve_credit.status = "released"
    session.commit()


def return_reserved_credit(
    session: Session, reserved_credit: ReservedCredit
) -> None:
    amount = reserved_credit.credits_reserved
    user = session.get(User, reserved_credit.user_id)
    get_credit(session, user.id, amount)  # type: ignore
    session.delete(reserved_credit)
    session.commit()
