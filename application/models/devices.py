from typing import Optional

from sqlmodel import Field

from ..lib.types import TABLE_ID
from ._base import Table


class DeviceType(Table, table=True):
    name: str
    read_address: Optional[bytes] = None
    read_command: Optional[bytes] = None
    read_length: Optional[bytes] = None
    write_address: Optional[bytes] = None
    write_command: Optional[bytes] = None
    write_bytes: Optional[list[bytes]] = None


class Device(Table, table=True):
    location: str
    name: str
    latitude: Optional[float]
    longitude: Optional[float]
    devicetype_id: TABLE_ID = Field(foreign_key="devicetype.id")
