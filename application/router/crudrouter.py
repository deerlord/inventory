from typing import Any, Callable, Coroutine, Optional, Type

from fastapi import Depends, HTTPException
from fastapi_crudrouter import SQLAlchemyCRUDRouter  # type: ignore
from pydantic import create_model
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

Model = SQLModel
PAGINATION = dict[str, Optional[int]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, list[Model]]]
CALLABLE = Callable[..., Coroutine[Any, Any, Model]]
NOT_FOUND = HTTPException(404, "Item not found")
SESSION = AsyncSession


class AsyncCRUDRouter(SQLAlchemyCRUDRouter):
    def __init__(self, model: Type[Model], db: Callable, prefix: str, tags=list[str]):
        super().__init__(
            schema=model,
            db_model=model,
            db=db,
            prefix=prefix,
            tags=tags,
        )

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        fields = {
            field.name: (Optional[field.type_], None)
            for field in self.db_model.__fields__.values()
            if field.name != self._pk
        }
        # error: No overload variant of "create_model" matches argument types "str", "Dict[Any, Tuple[object, None]]"
        # despite the "no overload" error, this is absolutely valid and seems to be
        # how the function is dynamically used
        params_model = create_model("Params", **fields)  # type: ignore

        async def route(
            # error: Variable "params_model" is not valid as a type
            # this works in the OpenAPI documentation though
            params: params_model = Depends(),  # type: ignore
            pagination: PAGINATION = self.pagination,
            db: SESSION = Depends(self.db_func),
        ) -> list[Model]:
            skip, limit = pagination.get("skip"), pagination.get("limit")
            statement = select(self.db_model)
            # error: params_model? has no attribute "dict"
            # as this is an instance of params_model it must have a .dict() method
            for key, value in params.dict().items():  # type: ignore
                if value is not None:  # prevents nullable field searches
                    statement = statement.where(getattr(self.db_model, key) == value)
            statement = (
                statement.order_by(getattr(self.db_model, self._pk))
                .limit(limit)
                .offset(skip)
            )
            results = await db.execute(statement)
            return results.scalars().all()

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, db: SESSION = Depends(self.db_func)  # type: ignore
        ) -> Model:
            statement = select(self.db_model).where(
                getattr(self.db_model, self._pk) == item_id
            )
            results = await db.execute(statement)
            items = results.scalars().all()
            if len(items) == 0:
                raise NOT_FOUND from None
            return items[0]

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
            db: SESSION = Depends(self.db_func),
        ) -> Model:
            db_model: Model = self.db_model(**model.dict())
            db.add(db_model)
            await db.commit()
            await db.refresh(db_model)
            return db_model

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
            model: self.update_schema,  # type: ignore
            db: SESSION = Depends(self.db_func),
        ) -> Model:
            coro = self._get_one()
            db_model: Model = await coro(item_id, db)

            for key, value in model.dict(exclude={self._pk}).items():
                if hasattr(db_model, key):
                    setattr(db_model, key, value)

            await db.commit()
            await db.refresh(db_model)

            return db_model

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(db: SESSION = Depends(self.db_func)) -> list[Model]:
            await db.execute(delete(self.db_model))
            await db.commit()

            coro = self._get_all()
            return await coro(db=db, pagination={"skip": 0, "limit": None})

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, db: SESSION = Depends(self.db_func)  # type: ignore
        ) -> Model:
            coro = self._get_one()
            db_model: Model = await coro(item_id, db)
            await db.delete(db_model)
            await db.commit()

            return db_model

        return route

    def __hash__(self):
        return hash(self.db_model)
