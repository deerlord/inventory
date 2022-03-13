from types import ModuleType
from typing import Iterable, Iterator, Type, Union

from fastapi import APIRouter, FastAPI
from sqlmodel import SQLModel

from application import models
from application.lib import database
from application.router.crudrouter import AsyncCRUDRouter
from application.lib import logging


__all__ = ["generate_routers", "include_routers"]


@logging.logger
def generate_routers() -> Iterator[APIRouter]:
    return map(generate_router, find_packages())


@logging.logger
def generate_router(package: ModuleType) -> APIRouter:
    prefix = package.__name__.replace("application.models.", "").lower()
    router = APIRouter(prefix=f"/{prefix}")
    crudrouters = map(crudrouter, find_data_models(package))
    include_routers(router, crudrouters)
    return router


@logging.logger
def find_packages() -> Iterator[ModuleType]:
    for pkg in dir(models):
        if not pkg.startswith("_") and pkg != "base":
            yield getattr(models, pkg)


@logging.logger
def find_data_models(package: ModuleType) -> Iterator[Type[SQLModel]]:
    trimmed = (
        getattr(package, model) for model in dir(package) if not model.startswith("_")
    )
    return filter(lambda m: hasattr(m, "__table__"), trimmed)


@logging.logger
def include_routers(
    top: Union[APIRouter, FastAPI], routers: Iterable[APIRouter]
) -> None:
    for router in routers:
        top.include_router(router)


@logging.logger
def crudrouter(model: Type[SQLModel]) -> AsyncCRUDRouter:
    return AsyncCRUDRouter(
        schema=model,
        db_model=model,
        db=database.connection,  # type: ignore
        prefix=f"/{model.__name__}",
        tags=[model.__name__],
    )
