from sqlite3 import IntegrityError
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

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


def engine() -> AsyncEngine:
    return create_async_engine(connection_string())


session = sessionmaker(engine(), expire_on_commit=False, class_=AsyncSession)


async def connection() -> AsyncGenerator[AsyncSession, None]:
    async with session() as _:
        try:
            yield _
            await _.commit()
        except IntegrityError:  # TODO: do something exception?
            await _.rollback()
