from enum import Enum
from typing import Optional

from pydantic import PositiveInt, conint
from sqlmodel import Field

from application.models.base import Table


class Medicine(Table, table=True):
    name: str


class Unit(str, Enum):
    mg = "mg"


class Container(Table, table=True):
    medicine_id: int = Field(foreign_key="medicine.id")
    size: Optional[PositiveInt] = None
    units: Optional[Unit] = None
    count: conint(ge=0)  # type: ignore
    max: PositiveInt = 1
