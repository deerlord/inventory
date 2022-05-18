from ipaddress import IPv4Address, IPv6Address
from typing import Optional

from application.models._base import Table


class RemoteDevice(Table):
    name: str
    location: str
    ipv4: Optional[IPv4Address]
    ipv6: Optional[IPv6Address]
    latitude: float
    longitude: float


class Sensor(RemoteDevice, table=True):
    ...
