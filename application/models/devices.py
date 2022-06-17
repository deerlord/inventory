from typing import Optional, Any

from application.models._base import Table


class Device(Table):
    location: str
    name: str
    latitude: Optional[float]
    longitude: Optional[float]
    read_address: int
    read_length: int = 1


class Sensor(Device, table=True):
    ...


class RemoteDevice(Table, table=True):
    write_address: int
    write_length: int = 1
    write_bytes: Optional[bytes] = None
