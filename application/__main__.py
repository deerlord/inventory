import os

import uvicorn  # type: ignore

from . import setup_application
from .settings import Settings


def main():
    host = os.environ.get("API_HOST")
    port = os.environ.get("API_POST")
    if host is None or port is None:
        raise RuntimeError(f"No host/port provided: host={host}, port={port}")
    settings = Settings()
    log_level = settings.log_level.lower()
    app = setup_application()
    kwargs = {
        "host": str(host),
        "port": int(port),
        "loop": "uvloop",
        "log_level": log_level,
        "use_colors": log_level == "DEBUG",
    }
    uvicorn.run(app, **kwargs)


if __name__ == "__main__":
    main()
