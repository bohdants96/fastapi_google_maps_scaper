from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.config import settings
from app.core.logs.logs import get_logger
from app.core.security import get_password_hash, verify_password
from app.models import (
    Message,
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter()

logger = get_logger()


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    logger.info(f"Creating new user {user_in}")
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        logger.error("The user with this email already exists in the system.")
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password,
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    logger.info("User created successfully.")
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    logger.info(f"Updating user {user_in}")
    if user_in.email:
        logger.error("Updating email")
        existing_user = crud.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != current_user.id:
            logger.error(
                "The user with this email already exists in the system."
            )
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    logger.info("User updated successfully.")
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    logger.info("Updating password.")
    if not verify_password(
        body.current_password, current_user.hashed_password
    ):
        logger.error("Incorrect password")
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        logger.error("New password cannot be the same as the current one")
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as the current one",
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    logger.info("Password updated successfully.")
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    logger.info("Getting current user.")
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    logger.info("Deleting user.")
    if current_user.is_superuser:
        logger.error("Super users are not allowed to delete themselves")
        raise HTTPException(
            status_code=403,
            detail="Super users are not allowed to delete themselves",
        )
    session.delete(current_user)
    session.commit()
    logger.info("User deleted successfully.")
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    logger.info(f"Creating new user {user_in}")
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        logger.error("The user with this email already exists in the system.")
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    logger.info("User created successfully.")
    return user
