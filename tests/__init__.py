import os

import pytest
from httpx import AsyncClient

from application import setup_application


@pytest.fixture
def setup():
    os.environ["DEBUG"] = "TRUE"
    os.environ["API_HOST"] = "localhost"
    os.environ["API_PORT"] = "8000"
    app = setup_application()
    yield app, AsyncClient(app=app, base_url="http://localhost:8000")
    if os.path.exists("./data.sqlite"):
        os.remove("./data.sqlite")
