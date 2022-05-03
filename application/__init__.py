import asyncio

from fastapi import APIRouter, FastAPI

from application.config import setup
from application.config.settings import Settings
from application.router import generate_routers, include_routers, middleware
from application.router._base import health_check


def setup_application() -> FastAPI:
    setup.logger()
    settings = Settings()
    results = asyncio.run(setup.setup_services())
    if not bool(results):
        message = ", ".join(results.failed_services)
        raise Exception(f"Unable to set up the following services: {message}")
    debug = settings.log_level == "DEBUG"
    app = FastAPI(debug=debug)
    api_router = APIRouter()
    include_routers(api_router, generate_routers())
    app.include_router(api_router)

    app.get("/health", tags=["Health"])(health_check)

    # middleware.testing(app)
    return app
