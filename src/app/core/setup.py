from collections.abc import AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from typing import Any

import anyio
import fastapi
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from ..middleware.logger_middleware import LoggerMiddleware
from ..models import *  # noqa: F403
from .config import AppSettings, CORSSettings, EnvironmentOption, EnvironmentSettings, PostgresSettings
from .config import settings as global_settings


async def set_threadpool_tokens(number_of_tokens: int = 100) -> None:
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = number_of_tokens


def lifespan_factory(
    settings: PostgresSettings | AppSettings | CORSSettings | EnvironmentSettings,
    create_tables_on_start: bool = False,
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator:
        await set_threadpool_tokens()
        yield

    return lifespan


def create_application(
    router: APIRouter,
    settings: PostgresSettings | AppSettings | CORSSettings | EnvironmentSettings,
    create_tables_on_start: bool = False,
    lifespan: Callable[[FastAPI], _AsyncGeneratorContextManager[Any]] | None = None,
    **kwargs: Any,
) -> FastAPI:
    if isinstance(settings, AppSettings):
        kwargs.update(
            {
                "title": settings.APP_NAME,
                "description": settings.APP_DESCRIPTION,
                "contact": {"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
                "license_info": {"name": settings.LICENSE_NAME},
                "version": settings.APP_VERSION,
            }
        )

    if isinstance(settings, EnvironmentSettings):
        kwargs.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    if lifespan is None:
        lifespan = lifespan_factory(settings, create_tables_on_start=create_tables_on_start)

    application = FastAPI(lifespan=lifespan, **kwargs)
    application.include_router(router)

    if isinstance(settings, CORSSettings):
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=settings.CORS_METHODS,
            allow_headers=settings.CORS_HEADERS,
        )
    application.add_middleware(LoggerMiddleware)

    if isinstance(settings, EnvironmentSettings) and settings.ENVIRONMENT != EnvironmentOption.PRODUCTION:
        docs_router = APIRouter()

        @docs_router.get("/docs", include_in_schema=False)
        async def get_swagger_documentation() -> fastapi.responses.HTMLResponse:
            return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

        @docs_router.get("/redoc", include_in_schema=False)
        async def get_redoc_documentation() -> fastapi.responses.HTMLResponse:
            return get_redoc_html(openapi_url="/openapi.json", title="docs")

        @docs_router.get("/openapi.json", include_in_schema=False)
        async def openapi() -> dict[str, Any]:
            return get_openapi(
                title=application.title,
                version=application.version or (global_settings.APP_VERSION or "0.1.0"),
                routes=application.routes,
            )

        application.include_router(docs_router)

    return application
