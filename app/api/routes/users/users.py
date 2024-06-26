
import datetime

from typing import Annotated, Any


from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi_pagination import LimitOffsetPage, paginate
from sqlmodel import select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.config import settings
from app.core.logs import get_logger
from app.core.security import get_password_hash, verify_password
from app.models import (
    Message,
    PublicSearchHistory,
    PublicTransaction,
    SearchHistory,
    Transaction,
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
    description="By this endpoint superuser can create other users, so superuser must be authorized",
)
def create_user(
    *,
    session: SessionDep,
    user_in: Annotated[
        UserCreate,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** user works correctly.",
                    "value": {
                        "email": "string@example.com",
                        "is_active": True,
                        "is_superuser": False,
                        "full_name": "string",
                        "mobile_phone": "+3800000000",
                        "instagram": "https://example.com/",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                        "password": "string12",
                    },
                },
            }
        ),
    ],
) -> Any:
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


@router.patch(
    "/me",
    response_model=UserPublic,
    description="By this endpoint user can update their own profile: email, full name, mobile phone, instagram, twitter, facebook, linkedin.",
)
def update_user_me(
    *,
    session: SessionDep,
    user_in: Annotated[
        UserUpdateMe,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** user works correctly.",
                    "value": {
                        "email": "string@example.com",
                        "full_name": "string",
                        "mobile_phone": "+380689999999",
                        "instagram": "https://example.com/",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                    },
                },
                "wrong phone number": {
                    "summary": "An example with wrong phone number",
                    "description": "Phone number must meet the standards",
                    "value": {
                        "email": "string@example.com",
                        "full_name": "string",
                        "mobile_phone": "06999999",
                        "instagram": "https://example.com/",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                    },
                },
                "wrong email": {
                    "summary": "An example with wrong email",
                    "description": "Email must have **@**",
                    "value": {
                        "email": "stringexample.com",
                        "full_name": "string",
                        "mobile_phone": "+380689999999",
                        "instagram": "https://example.com/",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                    },
                },
                "wrong url": {
                    "summary": "An example with wrong url",
                    "description": "URL must meet the standards.",
                    "value": {
                        "email": "string@example.com",
                        "full_name": "string",
                        "mobile_phone": "+380689999999",
                        "instagram": "instagram",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                    },
                },
            }
        ),
    ],
    current_user: CurrentUser,
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

    user_data = user_in.model_dump(exclude_unset=True, mode="json")

    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    logger.info("User updated successfully.")
    return current_user


@router.patch(
    "/me/password",
    response_model=Message,
    description="By this endpoint user can update the password.",
)
def update_password_me(
    *,
    session: SessionDep,
    body: Annotated[
        UpdatePassword,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** change password works correctly.",
                    "value": {
                        "current_password": "string12",
                        "new_password": "string34",
                    },
                },
                "same password": {
                    "summary": "Same passwords",
                    "description": "Password must be different from current password.",
                    "value": {
                        "current_password": "string12",
                        "new_password": "string12",
                    },
                },
                "wrong password": {
                    "summary": "Wrong password",
                    "description": "Password must meet the standards.",
                    "value": {
                        "current_password": "string12",
                        "new_password": "string",
                    },
                },
            },
        ),
    ],
    current_user: CurrentUser,
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
    current_user.last_password_reset_time = datetime.datetime.now()
    session.add(current_user)
    session.commit()
    logger.info("Password updated successfully.")
    return Message(message="Password updated successfully")


@router.get(
    "/me",
    response_model=UserPublic,
    description="This endpoint returns information about the current user if he is authorized.",
)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    logger.info("Getting current user.")
    return current_user


@router.delete(
    "/me",
    response_model=Message,
    description="This endpoint deletes the current user if he is authorized.",
)
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


@router.post(
    "/signup",
    response_model=UserPublic,
    description="By this endpoint user can register a new user.",
)
def register_user(
    session: SessionDep,
    user_in: Annotated[
        UserRegister,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** user works correctly.",
                    "value": {
                        "email": "string@example.com",
                        "full_name": "string",
                        "mobile_phone": "+380689999999",
                        "instagram": "https://example.com/",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                        "password": "string12",
                    },
                },
                "wrong phone number": {
                    "summary": "An example with wrong phone number",
                    "description": "Phone number must meet the standards",
                    "value": {
                        "email": "string@example.com",
                        "full_name": "string",
                        "mobile_phone": "06000000",
                        "instagram": "https://example.com/",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                        "password": "string12",
                    },
                },
                "wrong email": {
                    "summary": "An example with wrong email",
                    "description": "Email must have **@**",
                    "value": {
                        "email": "stringexample.com",
                        "full_name": "string",
                        "mobile_phone": "+380689999999",
                        "instagram": "https://example.com/",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                        "password": "string12",
                    },
                },
                "wrong password": {
                    "summary": "An example with wrong password",
                    "description": "Password must be at least 8 characters long and at most 20 characters long.",
                    "value": {
                        "email": "string@example.com",
                        "full_name": "string",
                        "mobile_phone": "+380689999999",
                        "instagram": "https://example.com/",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                        "password": "string",
                    },
                },
                "wrong url": {
                    "summary": "An example with wrong url",
                    "description": "URL must meet the standards.",
                    "value": {
                        "email": "string@example.com",
                        "full_name": "string",
                        "mobile_phone": "+380689999999",
                        "instagram": "instagram",
                        "twitter": "https://example.com/",
                        "facebook": "https://example.com/",
                        "linkedin": "https://example.com/",
                        "password": "string12",
                    },
                },
            }
        ),
    ],
) -> Any:
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

    user_data = user_in.model_dump(exclude_unset=True, mode="json")

    user_create = UserCreate.model_validate(user_data)
    user = crud.create_user(session=session, user_create=user_create)
    logger.info("User created successfully.")
    return user


@router.get(
    "/me/search-history",
    response_model=LimitOffsetPage[PublicSearchHistory],
    description="This endpoint returns search history for the authorized user.",
)
def get_search_history(
    session: SessionDep, current_user: CurrentUser
) -> LimitOffsetPage[PublicSearchHistory]:
    statement = select(SearchHistory).where(
        SearchHistory.user_id == current_user.id
    )
    search_history = session.exec(statement).all()
    return paginate(search_history)


@router.get(
    "/me/billing-history",
    response_model=LimitOffsetPage[PublicTransaction],
    description="This endpoint returns billing history for the authorized user.",
)
def get_billing_history(
    session: SessionDep, current_user: CurrentUser
) -> LimitOffsetPage[PublicTransaction]:
    statement = select(Transaction).where(
        Transaction.user_id == current_user.id
    )
    billing_history = session.exec(statement).all()
    return paginate(billing_history)
