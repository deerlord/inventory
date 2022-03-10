from application.database import Table


class Fresh(Table, table=True):
    name: str
    amount: int


class CannedGood(Table, table=True):
    name: str
    measurement: str
    amount: int
    count: int


class JarredGood(Table, table=True):
    ingredient: Fresh
    measurement: str
    amount: int
    count: int


class BulkGood(Table, table=True):
    ingredient: Fresh
    measurement: str
    amount: int
    count: int
