# TODO: improve import of error based on database type
from sqlite3 import IntegrityError

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from application.lib import cache

from ..settings import Settings

__all__ = ["engine", "connection"]


def connection_string(settings: Settings):
    strings = {
        "postgresql": (
            "postgresql://{database_username}:{database_password}"
            "@{database_hostname}:{database_port}/{database_name}"
        ),
        "sqlite": "sqlite+aiosqlite://{database_name}",
    }
    string = strings[settings.database_protocol]
    return string.format(**settings.dict())


@cache.singleton
def engine() -> AsyncEngine:
    settings = Settings()
    string = connection_string(settings)
    return create_async_engine(string)


async def connection():
    async with session() as local:
        try:
            yield local
        except IntegrityError:  # TODO: do something with exception?
            await local.rollback()


session = sessionmaker(engine(), expire_on_commit=False, class_=AsyncSession)
