import logging
from dataclasses import dataclass
from typing import Optional

from fastapi import FastAPI

from application.config import setup
from application.router import generate_routers, include_routers, middleware


def setup_application():
    logging.info("Setting up application...")
    results = setup.main()
    # TODO: parse results
    for name, result in results.dict().items():
        status = "COMPLETE" if result else "FAILED"
        logging.info(f"{name}: [{status}]")
    app = FastAPI()
    include_routers(app, generate_routers())
    middleware.acid_transaction(app)
    return app


@dataclass
class Logger:
    func: callable
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
