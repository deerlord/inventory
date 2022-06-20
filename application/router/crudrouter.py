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

PAGINATION = dict[str, Optional[int]]
CALLABLE_LIST = Callable[..., Coroutine[Any, Any, list[SQLModel]]]
CALLABLE = Callable[..., Coroutine[Any, Any, SQLModel]]
NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
ST = TypeVar("ST", Select, Delete)


class AsyncCRUDRouter(SQLAlchemyCRUDRouter):
    model: Type[SQLModel]

    def __init__(
        self, model: Type[SQLModel], db: Callable, prefix: str, tags=list[str]
    ):
        self.model = model
        super().__init__(
            schema=model,
            db_model=model,
            db=db,
            prefix=prefix,
            tags=tags,
        )

    @functools.cached_property
    def _search_model(self) -> BaseModel:
        fields = {}
        class_name = self.model.__name__.capitalize()
        for field in self.model.__fields__.values():
            if field.name != "id":
                has_default = (field.allow_none is True) is (field.default is None)
                default = field.default if has_default else ...
                fields[field.name] = (field.outer_type_, default)
        # mypy can't correctly type kwargs
        model = create_model(f"Search{class_name}", **fields)  # type: ignore
        return model

    async def _get_one_query(
        self,
        db: AsyncSession,
        item_id: Optional[int] = None,
        params: Optional[BaseModel] = None,
    ) -> Optional[SQLModel]:
        statement = select(self.model)
        if item_id:
            statement = statement.where(getattr(self.model, self._pk) == item_id)
        elif params:
            statement = self._where_clause(statement, params)
        else:
            message = f"No item_id or params specified to query for {self.model.__name__} data."
            raise Exception(message)
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
        statement = select(self.model)
        statement = self._where_clause(statement, params)
        statement = (
            statement.order_by(getattr(self.model, self._pk)).limit(limit).offset(skip)
        )
        results = await db.execute(statement)
        return results.scalars().all()

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            # error: Variable "params_model" is not valid as a type
            # this works in the OpenAPI documentation though
            # self._search_model,  # type: ignore
            pagination: PAGINATION = self.pagination,
            db: AsyncSession = Depends(self.db_func),
        ):
            skip, limit = pagination.get("skip"), pagination.get("limit")
            result = await self._get_many_query(db, skip, limit)
            return result

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type,  # type: ignore
            db: AsyncSession = Depends(self.db_func),
        ):
            result = await self._get_one_query(db, item_id=item_id)
            if result is None:
                detail = f"{self.model.__name__.lower()} not found"
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
            db_model = self.model(**model.dict())
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
            db: AsyncSession = Depends(self.db_func),
        ):
            statement = delete(self.model)
            statement = self._where_clause(statement)
            await db.execute(statement)
            await db.commit()

            result = await self._get_many_query(db)
            return result

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(
            item_id: self._pk_type, db: AsyncSession = Depends(self.db_func)  # type: ignore
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
                attr = getattr(self.model, key)
                retval = retval.where(attr == key)
        return retval

    def __hash__(self):
        return hash(self.model)

    def _default_checker(self, key: str, value: Any) -> bool:
        field = self.model.__fields__[key]
        # TODO: improve this check, as we might need to use default_factory for something
        conditions = (
            (field.allow_none is True) is (field.default is None),
            field.default_factory is None,
            field.default == value,
        )
        return all(conditions)
