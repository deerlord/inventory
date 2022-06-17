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

    async def _get_one_query(
        self,
        db: SESSION,
        item_id: Optional[int] = None,
        params: Optional[BaseModel] = None,
    ) -> SQLModel:
        statement = select(self.db_model)
        if item_id:
            statement = statement.where(getattr(self.db_model, self._pk) == item_id)
        elif params:
            statement = self._where_clause(statement, params)
        else:
            message = f"No item_id or params specified to query for model {self.db_model.__name__}."
            raise Exception(message)
        results = await db.execute(statement)
        items = results.scalars().all()
        if len(items) == 0:
            raise NOT_FOUND from None
        return items[0]

    async def _get_many_query(
        self,
        db: SESSION,
        skip: Optional[int] = 0,
        limit: Optional[int] = None,
        params: Optional[BaseModel] = None,
    ) -> list[SQLModel]:
        statement = select(self.db_model)
        statement = self._where_clause(statement, params)
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
            params: BaseModel = Depends(self._search_model),
            pagination: PAGINATION = self.pagination,
            db: SESSION = Depends(self.db_func),
        ):
            skip, limit = pagination.get("skip"), pagination.get("limit")
            result = await self._get_many_query(db, skip, limit)
            return result

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
            db: SESSION = Depends(self.db_func),
        ):
            result = await self._get_one_query(db, item_id=item_id)
            return result

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
            db: SESSION = Depends(self.db_func),
        ):
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
        ):
            db_model = await self._get_one_query(db, item_id=item_id)

            for key, value in model.dict(exclude={self._pk}).items():
                if hasattr(db_model, key):
                    setattr(db_model, key, value)

            await db.commit()
            await db.refresh(db_model)

            return db_model

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            params: BaseModel = Depends(self._search_model),
            db: SESSION = Depends(self.db_func),
        ):
            statement = delete(self.db_model)
            statement = self._where_clause(statement, params)
            await db.execute(statement)
            await db.commit()

            result = await self._get_many_query(db)
            return result

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, db: SESSION = Depends(self.db_func)  # type: ignore
        ):
            db_model = await self._get_one_query(db, item_id=item_id)
            await db.delete(db_model)
            await db.commit()

            return db_model

        return route

    def _where_clause(self, statement: ST, params: Optional[BaseModel] = None) -> ST:
        retval = statement
        if params:
            for key, value in params.dict().items():
                field = self._search_model.__fields__[key]
                conditions = (
                    (field.allow_none is True) is (field.default is None),
                    field.default_factory is None,
                    field.default == value,
                )
                if not all(conditions):
                    attr = getattr(self.db_model, key)
                    retval = retval.where(attr == key)
        return retval

    def __hash__(self):
        return hash(self.db_model)
