from fastapi import APIRouter

from app.api.routes import (
    login,
    users,
    utils,
    country,
    locations,
    business_types,
    scraped_data,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(country.router, prefix="/country", tags=["country"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(
    business_types.router, prefix="/business_types", tags=["business_types"]
)
api_router.include_router(
    scraped_data.router, prefix="/scraped-data", tags=["scraped_data"]
)
