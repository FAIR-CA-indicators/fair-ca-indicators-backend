import pytest

from fastapi.testclient import TestClient
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from app.main import app

@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)


@pytest.fixture
async def test_asyncclient():
    async with LifespanManager(app):
        # FIXME: Use setting
        async with AsyncClient(app=app, base_url="localhost:8000") as client:
            return client

