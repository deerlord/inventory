import functools
from typing import Any, Callable, Coroutine, Optional, Type, TypeVar

from fastapi import Depends, HTTPException
from fastapi_crudrouter import SQLAlchemyCRUDRouter  # type: ignore
from pydantic import BaseModel, create_model
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Delete, Select
from sqlmodel import SQLModel
from starlette import status

from ..lib import database
from ..models._base import SearchModel

PAGINATION = dict[str, Optional[int]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, list[SQLModel]]]
CALLABLE = Callable[..., Coroutine[Any, Any, SQLModel]]
NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
ST = TypeVar("ST", Select, Delete)


class AsyncCRUDRouter(SQLAlchemyCRUDRouter):
    sql_model: Type[SQLModel]

    def __init__(
        self,
        sql_model: Type[SQLModel],
    ):
        self.sql_model = sql_model
        model_name = sql_model.__name__
        category = sql_model.__module__.split(".")[-1]
        super().__init__(
            schema=sql_model,
            db_model=sql_model,
            db=database.connection,
            prefix=f"/{model_name}",
            tags=[category.capitalize()],
        )

    @functools.cached_property
    def _search_schema(self) -> Type[SearchModel]:
        fields = {}
        class_name = self.sql_model.__name__.capitalize()
        for field in self.sql_model.__fields__.values():
            fields[field.name] = (field.outer_type_ | None, None)
        fields.pop("id")
        model = create_model(
            f"Search{class_name}", __base__=SearchModel, **fields  # type: ignore
        )
        return model

    async def _get_one_query(
        self,
        db: AsyncSession,
        item_id: Optional[int] = None,
        params: Optional[BaseModel] = None,
    ) -> Optional[SQLModel]:
        statement = select(self.db_model)
        if item_id is not None:
            statement = statement.where(getattr(self.db_model, self._pk) == item_id)
        elif params is not None:
            statement = self._where_clause(statement, params)
        else:
            detail = f"No item_id or params specified to query for {self.sql_model.__name__} data."
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        results = await db.execute(statement)
        items = results.scalars().all()
        if len(items) == 0:
            return None
        return items[0]

    async def _get_many_query(
        self,
        db: AsyncSession,
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
            # mypy complains about self._search_schema, but API works as expected
            params: self._search_schema = Depends(),  # type: ignore
            pagination: PAGINATION = self.pagination,
            db: AsyncSession = Depends(self.db_func),
        ):
            skip, limit = pagination.get("skip"), pagination.get("limit")
            result = await self._get_many_query(db, skip, limit, params)
            return result

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
            db: AsyncSession = Depends(self.db_func),
        ):
            result = await self._get_one_query(db, item_id=item_id)
            if result is None:
                detail = f"{self.sql_model.__name__.lower()} not found"
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=detail
                )
            return result

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            model: self.create_schema,  # type: ignore
            db: AsyncSession = Depends(self.db_func),
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
            db: AsyncSession = Depends(self.db_func),
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
            # mypy complains about self._search_schema, but API works as expected
            params: self._search_schema = Depends(),  # type: ignore
            db: AsyncSession = Depends(self.db_func),
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
            item_id: self._pk_type,  # type: ignore
            db: AsyncSession = Depends(self.db_func),
        ):
            db_model = await self._get_one_query(db, item_id=item_id)
            await db.delete(db_model)
            await db.commit()

            return db_model

        return route

    def _where_clause(self, query: ST, params: Optional[BaseModel] = None) -> ST:
        statement = query
        clauses = []
        if params:
            for name, search_field in params.__fields__.items():
                search_value = getattr(params, name)
                if search_value is None:
                    continue
                attr = getattr(self.db_model, name)
                where = attr == search_value
                clauses.append(where)
            statement = statement.where(*clauses)
        return statement

    def __hash__(self):
        return hash(self.sql_model)
