import asyncio
import logging as base_logger

from fastapi import FastAPI

from application.config import setup
from application.config.settings import Settings
from application.router import generate_routers, include_routers


def setup_application():
    settings = Settings()
    results = asyncio.run(setup.setup_services())
    for service, success in results:
        message = f"{service.upper()}: {'COMPLETED' if success else 'FAILED'}"
        base_logger.info(message)
    # TODO: parse/log results of setup.main()
    app = FastAPI(debug=settings.debug)
    include_routers(app, generate_routers())
    return app
