import os

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
    _host = os.environ.get("API_HOST")
    _port = os.environ.get("API_POST")
    if None in {"host", "port"}:
        raise RuntimeError(f"No host/port provided: host={_host}, port={_port}")
    main(str(_host), int(_port))
