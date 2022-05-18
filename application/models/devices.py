from ipaddress import IPv4Address, IPv6Address
from typing import Optional

from application.models._base import Table


class RemoteDevice(Table):
    name: str
    location: str
    ipv4: Optional[IPv4Address]
    ipv6: Optional[IPv6Address]
    latitude: Optional[float]
    longitude: Optional[float]

    @property
    def identifier(self) -> str:
        return f"{self.location}::{self.name}"


class Sensor(RemoteDevice, table=True):
    ...


class Switch(RemoteDevice, table=True):
    state: bool
