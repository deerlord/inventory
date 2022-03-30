from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import PositiveInt, conint
from sqlmodel import Field

from application.models.base import Table


class Unit(str, Enum):
    tsp = "tsp"
    tbsp = "tbsp"
    ounce = "ounce"
    cup = "cup"
    pint = "pint"
    quart = "quart"
    gallon = "gallon"


class Ingredient(Table, table=True):
    name: str = Field(index=True)


class Item(Table):
    ingredient_id: PositiveInt = Field(foreign_key="ingredient.id")
    amount: PositiveInt
    units: Optional[Unit] = None
    packaged_on: datetime
    lifetime: timedelta


class StoredGood(Item):
    count: conint(ge=0)  # type: ignore


class FreshItem(Item, table=True):
    pass


class CannedGood(StoredGood, table=True):
    pass


class JarredGood(StoredGood, table=True):
    pass


class BulkGood(StoredGood, table=True):
    pass
