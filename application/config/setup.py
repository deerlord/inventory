from pydantic import BaseModel
from sqlmodel import SQLModel

from application.lib import database


async def setup_services() -> "ReturnData":
    db_done = await init_db()
    result = ReturnData(database=db_done)
    return result


class ReturnData(BaseModel):
    database: bool


async def init_db() -> bool:
    engine = database.engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    return True
