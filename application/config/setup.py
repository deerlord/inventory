import logging

from pydantic import BaseModel
from sqlmodel import SQLModel

from application.lib import database


async def main() -> "ReturnData":
    db_done = await init_db()
    result = ReturnData(database=db_done)
    return result


class ReturnData(BaseModel):
    database: bool


async def init_db() -> bool:
    retval = False
    try:
        engine = database.engine()
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        retval = True
    except Exception as error:
        logging.exception(error)
    return retval
