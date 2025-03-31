import pytest
from fastapi.testclient import TestClient
from app.main import app, links_db, original_url_index


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    links_db.clear()
    original_url_index.clear()

    yield

    links_db.clear()
    original_url_index.clear()
