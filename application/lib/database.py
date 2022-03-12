import functools
from sqlite3 import IntegrityError
from typing import AsyncGenerator, Union, Type, overload

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlmodel import Session

from application.config.settings import Settings


def connection_string():
    settings = Settings()
    strings = {
        "postgresql": (
            "postgresql://{database_username}:{database_password}"
            "@{database_hostname}:{database_port}/{database_name}"
        ),
        "sqlite": "sqlite://{database_name}",
    }
    return strings[settings.database_protocol].format(**settings.dict())


@functools.lru_cache(maxsize=2)
def engine() -> AsyncEngine:
    return create_async_engine(connection_string())


def session() -> AsyncSession:
    return AsyncSession(engine())


async def connection() -> AsyncGenerator[AsyncSession, None]:
    async with session() as _:
        try:
            yield _
            await _.commit()
        except IntegrityError as e:
            await _.rollback()
