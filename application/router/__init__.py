from types import ModuleType
from typing import Iterable, Iterator, List, Type, Union

from fastapi import APIRouter, FastAPI
from sqlmodel import SQLModel

from application import models
from application.lib import database
from application.router.crudrouter import AsyncCRUDRouter

__all__ = ["generate_routers", "include_routers"]


def generate_routers() -> Iterator[APIRouter]:
    return map(generate_router, find_packages())


def generate_router(package: ModuleType) -> APIRouter:
    prefix = package.__name__.replace("application.models.", "").lower()
    router = APIRouter(prefix=f"/{prefix}")
    data_models = list(find_data_models(package))
    create_items_route(router, data_models)
    crudrouters = map(crudrouter, data_models)
    include_routers(router, crudrouters)
    return router


def create_items_route(router: APIRouter, data_models: List[Type[SQLModel]]):
    names = [data_model.__name__ for data_model in data_models]
    prefix = router.prefix[1:]

    @router.get("", tags=["Items"], summary=f"Get {prefix.capitalize()} Items")
    async def get_items() -> List[str]:
        return names


def find_packages() -> Iterator[ModuleType]:
    for pkg in dir(models):
        if not pkg.startswith("_") and pkg != "base":
            yield getattr(models, pkg)


def find_data_models(package: ModuleType) -> Iterator[Type[SQLModel]]:
    trimmed = (
        getattr(package, model) for model in dir(package) if not model.startswith("_")
    )
    return filter(lambda m: hasattr(m, "__table__"), trimmed)


def include_routers(
    top: Union[APIRouter, FastAPI], routers: Iterable[APIRouter]
) -> None:
    for router in routers:
        top.include_router(router)


def crudrouter(model: Type[SQLModel]) -> AsyncCRUDRouter:
    return AsyncCRUDRouter(
        schema=model,
        db_model=model,
        db=database.connection,  # type: ignore
        prefix=f"/{model.__name__}",
        tags=[model.__name__],
    )
