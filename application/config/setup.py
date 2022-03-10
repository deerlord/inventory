from pydantic import BaseModel

from application import database


def main() -> "ReturnData":
    db_done = database.init()
    result = ReturnData(database=db_done)
    return result


class ReturnData(BaseModel):
    database: bool


if __name__ == "__main__":
    results = main()
    message = "".join(
        f"{step.upper()}: [{'COMPLETE' if result else 'FAILED'}]\n"
        for step, result in results.dict().items()
    )
    print(message)
