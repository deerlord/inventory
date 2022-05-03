from enum import Enum
from typing import Optional

from pydantic import PositiveInt, conint
from sqlmodel import Field

from application.models._base import Table


class Medicine(Table, table=True):
    name: str


class Unit(str, Enum):
    mg = "mg"


class Container(Table, table=True):
    medicine_id: Optional[PositiveInt] = Field(default=None, foreign_key="medicine.id")
    size: Optional[PositiveInt] = None
    units: Optional[Unit] = None
    count: conint(ge=0)  # type: ignore
    max: PositiveInt = 1
