from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import conint
from sqlmodel import Field

from ..lib.types import TABLE_ID
from ._base import Table


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
    ingredient_id: TABLE_ID = Field(default=None, foreign_key="ingredient.id")
    amount: int = 0
    units: Optional[Unit] = None
    packaged_on: Optional[datetime] = None
    lifetime: Optional[timedelta] = None
    expires: Optional[datetime] = None


class StoredGood(Item):
    count: conint(ge=0) = 0  # type: ignore


class FreshItem(Item, table=True):
    pass


class CannedGood(StoredGood, table=True):
    pass


class JarredGood(StoredGood, table=True):
    pass


class BulkGood(StoredGood, table=True):
    pass


class BoxedGood(StoredGood, table=True):
    pass
