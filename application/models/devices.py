from ipaddress import IPv4Address
from typing import Optional

from pydantic import validator

from application.models._base import Table


class RemoteDevice(Table, table=True):
    name: str
    location: str
    ipaddress: IPv4Address
    latitude: Optional[float]
    longitude: Optional[float]
    input_type: str

    @validator("input_type")
    def _input_type(cls, v):
        if v not in {"digital", "analog"}:
            raise Exception()
        return v
