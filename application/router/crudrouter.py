from fastapi_crudrouter import SQLAlchemyCRUDRouter


class AsyncCRUDRouter(SQLAlchemyCRUDRouter):
    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            pagination: PAGINATION = self.pagination,
        ) -> List[SQLModel]:
            skip, limit = pagination.get("skip"), pagination.get("limit")

            async with self.db_func():
                db_models: List[SQLModel] = await db.query(self.db_model)\
                    .order_by(getattr(self.db_model, self._pk))\
                    .limit(limit)\
                    .offset(skip)\
                    .all()
            return db_models

        return route
