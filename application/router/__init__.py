from types import ModuleType

from fastapi import APIRouter
from fastapi_crudrouter import SQLAlchemyCRUDRouter  # type: ignore

from application import models
from application.lib import database


def generate_routers():
    for package in packages():
        pkg_name = package.__name__.replace("application.models.", "").lower()
        router = APIRouter(prefix=f"/{pkg_name}")
        for model in inner_models(package):
            router.include_router(
                SQLAlchemyCRUDRouter(
                    schema=model,
                    db_model=model,
                    db=db_conn,
                    prefix=f"/{model.__name__}",
                    tags=[f"{model.__name__}s"],
                )
            )
        yield router


def packages():
    for pkg in dir(models):
        if not pkg.startswith("_") and pkg != "base":
            yield getattr(models, pkg)


def inner_models(package: ModuleType):
    trimmed = (
        getattr(package, model) for model in dir(package) if not model.startswith("_")
    )
    return filter(lambda m: hasattr(m, "__table__"), trimmed)


def db_conn():
    _ = database.session()
    try:
        yield _
        _.commit()
    finally:
        _.close()
