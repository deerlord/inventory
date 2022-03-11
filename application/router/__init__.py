from collections import Iterable
from types import ModuleType
from typing import Generator, Iterator, Type

from fastapi import APIRouter
from fastapi_crudrouter import SQLAlchemyCRUDRouter  # type: ignore
from sqlmodel import SQLModel

from application import models
from application.lib import database

__all__ = ["generate_routers"]


def generate_routers() -> Iterator[APIRouter]:
    return map(generate_router, packages())


def generate_router(package: ModuleType) -> APIRouter:
    pkg_name = package.__name__.replace("application.models.", "").lower()
    router = APIRouter(prefix=f"/{pkg_name}")
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


def include_routers(router: APIRouter, subrouters: Iterable[APIRouter]) -> None:
    for subrouter in subrouters:
        router.include_router(subrouter)


def crudrouter(model: Type[SQLModel]) -> SQLAlchemyCRUDRouter:
    return SQLAlchemyCRUDRouter(
        schema=model,
        db_model=model,
        db=db_conn,
        prefix=f"/{model.__name__}",
        tags=[f"{model.__name__}s"],
    )


def db_conn() -> Generator[database.Session, None, None]:
    _ = database.session()
    try:
        yield _
        _.commit()
    finally:
        _.close()
