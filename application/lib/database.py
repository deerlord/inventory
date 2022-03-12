import functools

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from application.config.settings import Settings


@functools.lru_cache(maxsize=1)
def engine() -> Engine:
    settings = Settings()
    return create_engine(f"{settings.database_protocol}://{settings.database_name}")


def session() -> Session:
    return Session(engine())
