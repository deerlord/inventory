from fastapi import Depends, HTTPException

from application.lib import database


async def health_check(db=Depends(database.connection)):
    try:
        await db.execute("SELECT 1")
    except Exception:
        raise HTTPException(500)
