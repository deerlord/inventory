import uvicorn  # type: ignore

from application import setup_application
from application.config.settings import Settings

if __name__ == "__main__":
    settings = Settings()
    app = setup_application()
    kwargs = {
        "host": "localhost",
        "port": 8001,
    }
    uvicorn.run(app, **kwargs)
