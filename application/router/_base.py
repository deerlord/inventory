from fastapi import Depends

from application.lib import database


async def health_check(db=Depends(database.connection)):
    await db.execute("SELECT 1")
