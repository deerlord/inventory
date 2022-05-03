from ipaddress import IPv4Address

from application.models._base import Table


class Sensor(Table, table=True):
    name: str
    location: str
    ipaddress: IPv4Address
    latitude: float
    longitude: float
