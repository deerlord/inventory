from types import ModuleType
from typing import Iterator, Type

from sqlmodel import SQLModel

from .. import models


def find_all_models() -> Iterator[Type[SQLModel]]:
    for package in find_packages():
        for model in find_data_models(package):
            yield model


def find_packages() -> Iterator[ModuleType]:
    for pkg in dir(models):
        if not pkg.startswith("_"):
            yield getattr(models, pkg)


def find_data_models(package: ModuleType) -> Iterator[Type[SQLModel]]:
    trimmed = (
        getattr(package, model) for model in dir(package) if not model.startswith("_")
    )
    return filter(lambda m: hasattr(m, "__table__"), trimmed)
