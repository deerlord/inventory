import uuid
from typing import List

from sqlmodel import Field, SQLModel
from sqlmodel import Field, Session, SQLModel, create_engine


class Ingredient(SQLModel, table=True):
    id: uuid = Field(default_factory=uuid.uuid4, primary_key=True)


def execute(protocol: str, database: str, operation: str, rows: List[SQLModel]):
    engine = create_engine(f"{protocol}://{database}")

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        operator = getattr(session, operation, None)
        if operator is None:
            raise Exception()
        for row in rows:
            operator(row)
        session.commit()
