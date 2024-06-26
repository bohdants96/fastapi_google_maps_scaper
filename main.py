import os

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.logs import get_logger


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )


def read_markdown(file_path):
    if not os.path.isfile(file_path):
        return "File not found."

    with open(file_path, "r") as file:
        description = file.read()

    return description


file_path = "description.md"
description = read_markdown(file_path)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    description=description,
)

add_pagination(app)

app.mount(
    "/static",
    StaticFiles(directory="./"),
    name="static",
)


@app.middleware("http")
async def log_stuff(request: Request, call_next):
    logger = get_logger("fastapi")
    response = await call_next(request)
    logger.debug(f"{request.method} {request.url} {response.status_code}")
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    errors: list[dict[str, str]] = [
        {
            "loc": " -> ".join(str(loc) for loc in err["loc"]),
            "msg": err["msg"],
            "type": err["type"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": errors},
    )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
