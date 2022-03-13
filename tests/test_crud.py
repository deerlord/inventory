import os
import random

import pytest
from fastapi.testclient import TestClient

from application import setup_application

ENDPOINT = "/food/ingredient"


@pytest.fixture
def client():
    os.environ["DEBUG"] = "TRUE"
    app = setup_application()
    yield TestClient(app)
    os.remove("tests/data.sqlite")


def test_get_all_but_none(client):
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    assert response.json() == []


def test_create(client):
    expected_id = 1
    expected_name = "garlic"
    expected_model = {"id": expected_id, "name": expected_name}
    response = client.post(ENDPOINT, json={"name": expected_name})
    assert response.status_code == 200
    assert response.json() == expected_model
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    assert response.json() == [expected_model]
    response = client.get(f"{ENDPOINT}/{expected_id}")
    assert response.status_code == 200
    assert response.json() == expected_model


def test_create_many(client):
    data = make_several(client)
    item_id = random.randrange(1, len(data))
    response = client.get(f"{ENDPOINT}/{item_id}")
    assert response.status_code == 200
    assert response.json() == data[item_id - 1]


def test_delete_one(client):
    data = make_several(client)
    item_id = random.randrange(1, len(data))
    response = client.delete(f"{ENDPOINT}/{item_id}")
    expected_delete = data.pop(item_id - 1)
    assert response.status_code == 200
    assert response.json() == expected_delete
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    assert response.json() == data
    response = client.get(f"{ENDPOINT}/{item_id}")
    assert response.status_code == 404


def test_delete_all(client):
    make_several(client)
    for method in (client.delete, client.get):
        response = method(ENDPOINT)
        assert response.status_code == 200
        assert response.json() == []


def make_several(client: TestClient, count: int = 10) -> list:
    data = []
    for item_id in range(1, count):
        json = {"id": item_id, "name": f"name_{item_id}"}
        response = client.post(ENDPOINT, json=json)
        assert response.status_code == 200
        assert response.json() == json
        data.append(json)
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    assert response.json() == data
    return data
