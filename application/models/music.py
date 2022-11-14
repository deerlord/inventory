from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field

from ..lib.types import TABLE_ID
from ._base import Table


class Filetype(str, Enum):
    mp3 = "mp3"
    wav = "wav"


class Artist(Table, table=True):
    name: str


class Album(Table, table=True):
    artist_id: TABLE_ID = Field(default=None, foreign_key="artist.id")
    name: str
    released: datetime


class Track(Table, table=True):
    album_id: Optional[TABLE_ID] = Field(default=None, foreign_key="album.id")
    title: str
    path: str
    filetype: Filetype
    length: int
