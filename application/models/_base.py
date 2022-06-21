from typing import Optional

from pydantic.main import BaseModel
from sqlmodel import Field, SQLModel

from ..lib.types import TABLE_ID


class Table(SQLModel):
    id: Optional[TABLE_ID] = Field(default=None, primary_key=True)


class SearchModel(BaseModel):
    class Config:
        validate_assignment = True
