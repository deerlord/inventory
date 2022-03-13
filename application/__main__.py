import uvicorn  # type: ignore

from application import setup_application
from application.config.settings import Settings


if __name__ == "__main__":
    settings = Settings()
    log_level = "debug" if settings.debug else "info"
    app = setup_application()
    uvicorn.run(app, host="localhost", port=8000, log_level=log_level)
