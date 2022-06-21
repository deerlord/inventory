from fastapi import APIRouter

from ..lib import models as libmodels
from .crudrouter import AsyncCRUDRouter


def crud_router() -> APIRouter:
    router = APIRouter()
    for package in libmodels.find_packages():
        prefix = package.__name__.replace("application.models.", "").lower()
        pkg_router = APIRouter(prefix=f"/{prefix}")
        for model in libmodels.find_data_models(package):
            crud = AsyncCRUDRouter(sql_model=model)
            pkg_router.include_router(crud)
        router.include_router(pkg_router)
    return router
