import datetime
import re
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi_pagination import LimitOffsetPage, paginate
from sqlmodel import select
from starlette.responses import JSONResponse

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.config import settings
from app.core.logs import get_logger
from app.core.security import get_password_hash, verify_password
from app.models import (
    BusinessLead,
    BusinessOwnerInfo,
    Message,
    PeopleLead,
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


def verify_url(url, pattern):
    # Use the re.match function to check if the URL matches the pattern
    if re.match(pattern, url):
        return True
    else:
        return False


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    description="By this endpoint superuser can create other users, so superuser must be authorized",
    include_in_schema=False,
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

    if user_in.linkedin and len(user_in.linkedin) > 0:
        test_linkedin = verify_url(
            user_in.linkedin, pattern=r"^https://www\.linkedin\.com(/.*)?$"
        )
        if not test_linkedin:
            raise HTTPException(
                status_code=400, detail="linkedin is not correct"
            )

    if user_in.twitter and len(user_in.twitter) > 0:
        test_twitter = verify_url(
            user_in.twitter, pattern=r"^https://x\.com(/.*)?$"
        )
        if not test_twitter:
            raise HTTPException(
                status_code=400, detail="twitter is not correct"
            )

    if user_in.facebook and len(user_in.facebook) > 0:
        test_facebook = verify_url(
            user_in.facebook, pattern=r"^https://www\.facebook\.com(/.*)?$"
        )
        if not test_facebook:
            raise HTTPException(
                status_code=400, detail="facebook is not correct"
            )

    if user_in.instagram and len(user_in.instagram) > 0:
        test_instagram = verify_url(
            user_in.instagram, pattern=r"^https://www\.instagram\.com(/.*)?$"
        )
        if not test_instagram:
            raise HTTPException(
                status_code=400, detail="instagram is not correct"
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
                        "avatar_url": "https://via.placeholder.com/124",
                        "city": "test",
                        "country": "test",
                        "about_description": "test",
                        "occupation": "test",
                        "company": "test",
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
    statement = (
        select(SearchHistory)
        .where(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.search_time.desc(), SearchHistory.id.desc())
    )
    search_history = session.exec(statement).all()
    return paginate(search_history)


@router.get(
    "/me/search-history/{search_history_id}",
    description="This endpoint returns one search history for the authorized user by id.",
)
def get_one_search_history(
    session: SessionDep, current_user: CurrentUser, search_history_id: int
) -> Any:
    statement = select(SearchHistory).where(
        SearchHistory.user_id == current_user.id,
        SearchHistory.id == search_history_id,
    )
    search_history = session.exec(statement).first()
    if not search_history:
        return JSONResponse(
            {"message": "No search history found."}, status_code=404
        )
    internal_searches = []
    for internal_search_id in search_history.internal_search_ids[
        "internal_search_ids"
    ]:
        if search_history.source == "business":
            statement = select(BusinessLead).where(
                BusinessLead.id == internal_search_id,
            )
            internal_search = session.exec(statement).first()
            internal_search = internal_search.dict()

            if internal_search:
                internal_searches.append(internal_search)
        else:
            statement = select(PeopleLead).where(
                PeopleLead.id == internal_search_id,
            )
            internal_search = session.exec(statement).first()
            internal_search = internal_search.dict()

            statement = select(BusinessOwnerInfo).where(
                BusinessOwnerInfo.business_lead_id == internal_search_id
            )
            business_owner_info = session.exec(statement).first()

            if internal_search:
                internal_search["employee"] = business_owner_info
                internal_searches.append(internal_search)
    result = {
        "user_id": search_history.user_id,
        "search_time": search_history.search_time,
        "internal_search": internal_searches,
        "credits_used": search_history.credits_used,
        "source": search_history.source,
        "task_id": search_history.task_id,
        "status": search_history.status,
    }
    return result


@router.get(
    "/me/billing-history",
    response_model=LimitOffsetPage[PublicTransaction],
    description="This endpoint returns billing history for the authorized user.",
    include_in_schema=False,
)
def get_billing_history(
    session: SessionDep, current_user: CurrentUser
) -> LimitOffsetPage[PublicTransaction]:
    statement = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc(), Transaction.id.desc())
    )
    billing_history = session.exec(statement).all()
    return paginate(billing_history)
