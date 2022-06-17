from typing import Any, Callable, Coroutine, Optional, Type, TypeVar

from fastapi import Depends, HTTPException
from fastapi_crudrouter import SQLAlchemyCRUDRouter  # type: ignore
from pydantic import BaseModel, create_model
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Delete, Select
from sqlmodel import SQLModel


Model = SQLModel
PAGINATION = dict[str, Optional[int]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, list[Model]]]
CALLABLE = Callable[..., Coroutine[Any, Any, Model]]
NOT_FOUND = HTTPException(404, "Item not found")
SESSION = AsyncSession
DT = TypeVar("DT")
ST = TypeVar("ST", Select, Delete)


class AsyncCRUDRouter(SQLAlchemyCRUDRouter):
    def __init__(self, model: Type[Model], db: Callable, prefix: str, tags=list[str]):
        fields = {
            field.name: (Optional[field.type_], None)
            for field in model.__fields__.values()
            if field.name != "id"
        }
        # error: No overload variant of "create_model" matches argument types "str", "Dict[Any, Tuple[object, None]]"
        # despite the "no overload" error, this is absolutely valid and seems to be
        # how the function is dynamically used
        self._search_model = create_model(f"Search{model.__name__.capitalize()}", **fields)  # type: ignore
        super().__init__(
            schema=model,
            db_model=model,
            db=db,
            prefix=prefix,
            tags=tags,
        )

    def _model(self):
        return self.db_model

    def _queries(self):
        return self._search_model

    @staticmethod
    async def _get_one_query(
        db_model: DT,
        primary_key: str,
        item_id: Any,
        db: SESSION,
    ) -> DT:
        statement = select(db_model).where(getattr(db_model, primary_key) == item_id)
        results = await db.execute(statement)
        items = results.scalars().all()
        if len(items) == 0:
            raise NOT_FOUND from None
        return items[0]

    async def _get_many_query(
        self,
        db_model: DT,
        db: SESSION,
        skip: Optional[int] = 0,
        limit: Optional[int] = 0,
    ) -> list[DT]:
        statement = select(db_model)
        statement = (
            statement.order_by(getattr(self.db_model, self._pk))
            .limit(limit)
            .offset(skip)
        )
        results = await db.execute(statement)
        return results.scalars().all()

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            # error: Variable "params_model" is not valid as a type
            # this works in the OpenAPI documentation though
            params: BaseModel = Depends(self._queries),
            pagination: PAGINATION = self.pagination,
            db: SESSION = Depends(self.db_func),
        ) -> list[DT]:
            skip, limit = pagination.get("skip"), pagination.get("limit")
            results = await self._get_many_query(self.db_model, db, skip, limit)
            return results

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
            db: SESSION = Depends(self.db_func),
        ) -> DT:
            result = await self._get_one_query(self.db_model, self._pk, item_id, db)
            return result

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
            db: SESSION = Depends(self.db_func),
            _data_model: DT = self.db_model,
        ) -> DT:
            db_model = self.db_model(**model.dict())
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
        ) -> DT:
            db_model = await self._get_one_query(self.db_model, self._pk, item_id, db)

            for key, value in model.dict(exclude={self._pk}).items():
                if hasattr(db_model, key):
                    setattr(db_model, key, value)

            await db.commit()
            await db.refresh(db_model)

            return db_model

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            params: BaseModel = Depends(),
            db: SESSION = Depends(self.db_func),
        ) -> list[DT]:
            statement = delete(self.db_model)
            statement = self._where_clause(statement, params)
            await db.execute(statement)
            await db.commit()

            result = await self._get_many_query(self.db_model, db, 0, None)
            return result

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, db: SESSION = Depends(self.db_func), _data_model: DT = self.db_model  # type: ignore
        ) -> DT:
            db_model = await self._get_one_query(self.db_model, self._pk, item_id, db)
            await db.delete(db_model)
            await db.commit()

            return db_model

        return route

    def __hash__(self):
        return hash(self.db_model)

    def _where_clause(self, statement: ST, params: BaseModel = None) -> ST:
        retval = statement
        if isinstance(params, BaseModel):
            for key, value in params.dict().items():
                field = params.__fields__[key]
                conditions = (
                    # checks if we have a queriable .default
                    (field.allow_none is True) is (field.default is None),
                    # checks we don't fall back to a factory instead
                    field.default_factory is None,
                    # we actually have the default value
                    field.default == value,
                )
                if not all(conditions):
                    attr = getattr(self.db_model, key)
                    retval = retval.where(attr == key)
        return retval
