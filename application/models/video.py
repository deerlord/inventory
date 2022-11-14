from datetime import datetime
from sqlmodel import Field

from ..lib.types import TABLE_ID
from ._base import Table
from enum import Enum


class Filetype(str, Enum):
    avi = "avi"
    mkv = "mkv"


class Video(Table, table=True):
    name: str
    path: str
    filetype: Filetype
    length: int
    released: datetime


class Season(Table, table=True):
    videos: list[TABLE_ID] = Field(default_factory=list, foreign_key="video.id")


class TVShow(Table, table=True):
    name: str
    seasons: list[TABLE_ID] = Field(default_factory=list, foreign_key="season.id")
