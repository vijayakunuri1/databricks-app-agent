from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import get_settings
from api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Databricks Unity Catalog API",
        description="REST API over Unity Catalog via Databricks Apps",
        version=settings.app_version,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # All routes MUST be under /api prefix for Databricks Apps OAuth2 to work
    app.include_router(api_router, prefix="/api")

    # Serve chat UI — mount AFTER api router so /api/* takes priority
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

    return app


app = create_app()
