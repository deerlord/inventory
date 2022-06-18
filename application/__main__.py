import sys

import uvicorn  # type: ignore

from . import setup_application
from .settings import Settings


def main(host: str, port: int):
    settings = Settings()
    app = setup_application()
    kwargs = {
        "host": host,
        "port": port,
        "loop": "uvloop",
        "log_level": settings.log_level.lower(),
    }
    if settings.log_level != "DEBUG":
        kwargs["use_colors"] = False
    uvicorn.run(app, **kwargs)


if __name__ == "__main__":
    host = str(sys.argv[1])
    port = int(sys.argv[2])
    main(host, port)
