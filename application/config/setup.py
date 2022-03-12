import logging

from pydantic import BaseModel
from sqlmodel import SQLModel

from application.lib import database


def main() -> "ReturnData":
    db_done = init_db()
    result = ReturnData(database=db_done)
    return result


class ReturnData(BaseModel):
    database: bool


def init_db() -> bool:
    retval = False
    try:
        engine = database.engine()
        SQLModel.metadata.create_all(engine)
        retval = True
    except Exception as error:
        logging.exception(error)
    return retval

