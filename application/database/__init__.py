import logging
import uuid
from typing import List, Optional

from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel, create_engine

from application.config.settings import Settings


def generate_uuid() -> int:
    return uuid.uuid4().int


class Table(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)


def engine() -> Engine:
    settings = Settings()
    return create_engine(f"{settings.database_protocol}://{settings.database_name}")


def init() -> bool:
    retval = False
    try:
        SQLModel.metadata.create_all(engine())
        retval = True
    except Exception as error:
        logging.exception(error)
    return retval


def execute(operation: str, rows: List[SQLModel]):
    with Session(engine()) as session:
        operator = getattr(session, operation, None)
        if operator is None:
            raise Exception()
        for row in rows:
            operator(row)
        session.commit()
