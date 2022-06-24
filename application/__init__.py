import asyncio

from fastapi import FastAPI
from sqlmodel import SQLModel

from .lib import database
from .router import crud_router, health
from .settings import Settings


def setup_application(*args, **kwargs) -> FastAPI:
    settings = Settings()
    success = asyncio.run(init_database())
    if not success:
        message = (
            f"Unable to initialize database {settings.database_name} on startup,"
            f" using protocol {settings.database_protocol}"
            f" and driver {settings.database_driver}"
        )
        raise Exception(message)
    debug = settings.log_level == "DEBUG"
    app = FastAPI(debug=debug)
    top_router = crud_router()
    app.include_router(top_router)
    app.get("/health", tags=["Health"])(health.check)

    return app


async def init_database():
    engine = database.engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    return True
