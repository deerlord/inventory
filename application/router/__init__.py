from types import ModuleType
from typing import Generator, Iterator, Type

from fastapi import APIRouter
from fastapi_crudrouter import SQLAlchemyCRUDRouter  # type: ignore
from sqlmodel import SQLModel

from application import models
from application.lib import database


def generate_routers() -> Iterator[APIRouter]:
    for package in packages():
        pkg_name = package.__name__.replace("application.models.", "").lower()
        router = APIRouter(prefix=f"/{pkg_name}")
        for model in data_models(package):
            crudrouter = SQLAlchemyCRUDRouter(
                schema=model,
                db_model=model,
                db=db_conn,
                prefix=f"/{model.__name__}",
                tags=[f"{model.__name__}s"],
            )
            router.include_router(crudrouter)
        yield router


def packages() -> Iterator[ModuleType]:
    for pkg in dir(models):
        if not pkg.startswith("_") and pkg != "base":
            yield getattr(models, pkg)


def data_models(package: ModuleType) -> Iterator[Type[SQLModel]]:
    trimmed = (
        getattr(package, model) for model in dir(package) if not model.startswith("_")
    )
    return filter(lambda m: hasattr(m, "__table__"), trimmed)


def db_conn() -> Generator[database.Session, None, None]:
    _ = database.session()
    try:
        yield _
        _.commit()
    finally:
        _.close()
