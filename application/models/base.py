from typing import Optional

from pydantic import PositiveInt
from sqlmodel import Field, SQLModel


class Table(SQLModel):
    id: Optional[PositiveInt] = Field(default=None, primary_key=True)
