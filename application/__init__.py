import asyncio

from fastapi import FastAPI
from sqlmodel import SQLModel

from .lib import database
from .router import crud_router, health
from .settings import Settings


def setup_application() -> FastAPI:
    settings = Settings()
    asyncio.run(init_database())
    debug = settings.log_level.upper() == "DEBUG"
    app = FastAPI(debug=debug, root_path="/inventory")
    top_router = crud_router()
    app.include_router(top_router)
    app.get("/health", tags=["Health"])(health.check)
    return app


async def init_database():
    engine = database.engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
