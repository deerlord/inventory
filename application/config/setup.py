import logging
from typing import List

from pydantic import BaseModel
from sqlmodel import SQLModel

from application.lib import database


async def setup_services() -> "ReturnData":
    db_done = await init_database()
    return ReturnData(database=db_done)


class ReturnData(BaseModel):
    database: bool

    @property
    def failed_services(self) -> List[str]:
        return [service for service, success in self.dict().items() if not success]

    def __str__(self):
        return "\n".join(
            f"{service.upper()}: {'COMPLETED' if success else 'FAILED'}"
            for service, success in self.dict().items()
        )

    def __bool__(self):
        return len(self.failed_services) == 0


async def init_database():
    engine = database.engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    return True


def logger():
    requests = logging.getLogger("requests")
    return requests
