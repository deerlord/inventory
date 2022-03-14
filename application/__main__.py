import uvicorn  # type: ignore

from application import setup_application
from application.config.settings import Settings

if __name__ == "__main__":
    settings = Settings()
    app = setup_application()
    kwargs = {
        "log_level": "info",
        "host": "localhost",
        "port": 8000,
        "reload": False,
        "loop": "uvloop",
    }
    if settings.debug:
        kwargs.update({"reload": True, "log_level": "debug"})
    uvicorn.run(app, **kwargs)
