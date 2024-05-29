from fastapi import APIRouter

from app.api.internal import scraper
from app.api.routes.login import login
from app.api.routes.scraped_data import scraped_data
from app.api.routes.users import users
from app.api.routes.utils import utils

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
