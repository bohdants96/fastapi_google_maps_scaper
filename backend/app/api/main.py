from fastapi import APIRouter

from app.api.routes import items, login, users, utils, country, locations, business_types

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(country.router, prefix="/country", tags=["country"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(business_types.router, prefix="/business_types", tags=["business_types"])