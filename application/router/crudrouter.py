from typing import Any, Callable, Coroutine, Dict, List, Optional

from fastapi import Depends, HTTPException
from fastapi_crudrouter import SQLAlchemyCRUDRouter  # type: ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

Model = SQLModel
PAGINATION = Dict[str, Optional[int]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, List[Model]]]
CALLABLE = Callable[..., Coroutine[Any, Any, Model]]
NOT_FOUND = HTTPException(404, "Item not found")
SESSION = AsyncSession


class AsyncCRUDRouter(SQLAlchemyCRUDRouter):
    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            pagination: PAGINATION = self.pagination,
            db: SESSION = Depends(self.db_func),
        ) -> List[Model]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            results = await db.execute(
                select(self.db_model)
                .order_by(getattr(self.db_model, self._pk))
                .limit(limit)
                .offset(skip)
            )
            return results.scalars().all()

        return route
