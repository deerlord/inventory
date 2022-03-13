from sqlite3 import IntegrityError
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from application.config.settings import Settings


def connection_string(settings: Settings):
    strings = {
        "postgresql": (
            "postgresql://{database_username}:{database_password}"
            "@{database_hostname}:{database_port}/{database_name}"
        ),
        "sqlite": "sqlite+aiosqlite://{database_name}",
    }
    return strings[settings.database_protocol].format(**settings.dict())


def engine() -> AsyncEngine:
    settings = Settings()
    string = connection_string(settings)
    return create_async_engine(string)


session = sessionmaker(engine(), expire_on_commit=False, class_=AsyncSession)


async def connection() -> AsyncGenerator[AsyncSession, None]:
    async with session() as _:
        try:
            yield _
        except IntegrityError:  # TODO: do something exception?
            await _.rollback()


def sync_engine() -> Engine:
    settings = Settings()
    string = connection_string(settings)
    return create_engine(string)
