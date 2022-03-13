import asyncio
import logging
from dataclasses import dataclass
from typing import Callable, Optional

from fastapi import FastAPI

from application.config import setup
from application.router import generate_routers, include_routers


def setup_application():
    asyncio.run(setup.main())
    # TODO: parse/log results of setup.main()
    app = FastAPI()
    include_routers(app, generate_routers())
    return app


@dataclass
class Logger:
    func: Callable
    _log_name: Optional[str] = None

    def __post_init__(self):
        self._log_name = " ".join(
            word.capitalize() for word in self.func.__name__.replace("_", "").split(" ")
        )

    async def __async_call(self, *args, **kwargs):
        logging.info(self._log_name)
        result = await self.func(*args, **kwargs)
        return result

    def __sync_call__(self, *args, **kwargs):
        logging.info(self._log_name)
        result = self.func(*args, **kwargs)
        return result
