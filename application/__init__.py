import asyncio
import logging
from dataclasses import dataclass
from typing import Callable, Optional

from fastapi import FastAPI

from application.config import setup
from application.router import generate_routers, include_routers
from application.lib import logging


@logging.logger
def setup_application():
    results = asyncio.run(setup.setup_services())
    for service, success in results:
        message = f"{service.upper()}: {'COMPLETED' if success else 'FAILED'}"
        print(message)
    # TODO: parse/log results of setup.main()
    app = FastAPI()
    include_routers(app, generate_routers())
    return app
