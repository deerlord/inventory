import logging
import sys
from copy import deepcopy

import uvicorn  # type: ignore

from application import setup_application
from application.config.settings import Settings

if __name__ == "__main__":
    settings = Settings()
    app = setup_application()
    port = sys.argv[1]
    kwargs = {
        "host": "localhost",
        "port": port,
    }
    if settings.debug:
        kwargs.update({"reload": True, "log_level": logging.DEBUG})
    log_config = deepcopy(uvicorn.config.LOGGING_CONFIG)
    log_config["disable_existing_loggers"] = False
    uvicorn.run(app, log_config=log_config, **kwargs)
