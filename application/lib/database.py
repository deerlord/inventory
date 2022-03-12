import functools

from sqlalchemy.engine import Engine
from sqlmodel import AsyncSession, create_async_engine

from application.config.settings import Settings
import asyncio


ACID = asyncio.Lock()


@functools.lru_cache(maxsize=1)
def engine() -> Engine:
    settings = Settings()
    return create_async_engine(f"{settings.database_protocol}://{settings.database_name}")


def session() -> AsyncSession:
    return AsyncSession(engine())


async def connection() -> Generator[database.Session, None, None]:
    async with ACID:
        _ = database.session()
        try:
            yield _
            _.commit()
        finally:
            _.close()
