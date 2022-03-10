from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlmodel import Session

from application.config.settings import Settings


def engine() -> Engine:
    settings = Settings()
    return create_engine(f"{settings.database_protocol}://{settings.database_name}")


def session() -> Session:
    return Session(engine())
