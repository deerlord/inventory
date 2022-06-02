import asyncio

from fastapi import FastAPI
from sqlmodel import SQLModel

from application.lib import database
from application.router import crud_router
from application.router._base import health_check
from application.settings import Settings


def setup_application() -> FastAPI:
    settings = Settings()
    results = asyncio.run(init_database())
    if not bool(results):
        message = ", ".join(results.failed_services)
        raise Exception(f"Unable to set up the following services: {message}")
    debug = settings.log_level == "DEBUG"
    app = FastAPI(debug=debug)
    app.include_router(crud_router())
    app.get("/health", tags=["Health"])(health_check)

    # middleware.testing(app)
    return app


async def init_database():
    engine = database.engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    return True
