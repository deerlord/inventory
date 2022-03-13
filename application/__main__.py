import asyncio

import uvicorn  # type: ignore

from application import setup_application
from application.config import setup

if __name__ == "__main__":
    setup_results = asyncio.run(setup.main())
    # parse setup results
    app = setup_application()
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")
