from fastapi import Depends, HTTPException, status

from ..lib import database


async def check(db: database.SESSION = Depends(database.connection)):
    try:
        await db.execute("SELECT 1")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
