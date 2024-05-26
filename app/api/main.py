from fastapi import APIRouter

from app.api.routes import (
    login,
    scraped_data,
    users,
    utils,
)

from app.api.internal import scraper

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(
    scraped_data.router, prefix="/scraped-data", tags=["scraped_data"]
)

api_router.include_router(
    scraper.router, prefix="/internal", tags=["internal-apis"]
)
