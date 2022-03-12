from collections import Iterable
from types import ModuleType
from typing import Generator, Iterator, Type, Union

from fastapi import APIRouter, FastAPI
from fastapi_crudrouter import SQLAlchemyCRUDRouter  # type: ignore
from sqlmodel import SQLModel

from application import models
from application.lib import database
from application.router.crudrouter import AsyncCRUDRouter


__all__ = ["generate_routers", "include_routers"]


def generate_routers() -> Iterator[APIRouter]:
    return map(generate_router, packages())


def generate_router(package: ModuleType) -> APIRouter:
    prefix = package.__name__.replace("application.models.", "").lower()
    router = APIRouter(prefix=f"/{prefix}")
    crudrouters = map(crudrouter, data_models(package))
    include_routers(router, crudrouters)
    return router


def packages() -> Iterator[ModuleType]:
    for pkg in dir(models):
        if not pkg.startswith("_") and pkg != "base":
            yield getattr(models, pkg)


def data_models(package: ModuleType) -> Iterator[Type[SQLModel]]:
    trimmed = (
        getattr(package, model) for model in dir(package) if not model.startswith("_")
    )
    return filter(lambda m: hasattr(m, "__table__"), trimmed)


def include_routers(
    top: Union[APIRouter, FastAPI], routers: Iterable[APIRouter]
) -> None:
    for routers in routers:
        top.include_router(routers)


def crudrouter(model: Type[SQLModel]) -> AsyncCRUDRouter:
    return AsyncCRUDRouter(
        schema=model,
        db_model=model,
        db=database.connection,
        prefix=f"/{model.__name__}",
        tags=[f"{model.__name__}s"],
        get_one_route=False,
        create_route=False,
        update_route=False,
        delete_one_route=False,
        delete_all_route=False
    )

