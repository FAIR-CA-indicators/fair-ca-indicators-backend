import pytest
import os
from redis import Redis, ConnectionError

from fastapi.testclient import TestClient
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from app.main import app


# FIXME: This is a crude way to make sure we are in test environment...
#   A better way would be to find how to set the environment
@pytest.fixture(scope="session", autouse=True)
def test_env():
    assert (
        os.environ.get("FAIR_COMBINE_ENV") == "test"
    ), "FAIR_COMBINE_ENV environment variable must be set to 'test'"


@pytest.fixture(scope="session")
def test_redis():
    redis_test = Redis(
        host=os.environ.get("REDIS_URL", "localhost"),
        port=os.environ.get("REDIS_PORT", 6379),
        db=15,  # Using the last db for tests
        # FIXME
        # username=os.environ.get("REDIS_USERNAME", "default"),
        # password=os.environ.get("REDIS_PASSWORD", "")
        decode_responses=True,
    )
    try:
        # Check that connection is working
        redis_test.ping()
    except ConnectionError as e:
        raise ConnectionError(f"An error occurred with redis server: {str(e)}")
    return redis_test


@pytest.fixture
def redis_client(test_redis):
    yield test_redis
    test_redis.flushdb()


@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)


@pytest.fixture
async def test_asyncclient():
    async with LifespanManager(app):
        # FIXME: Use setting
        async with AsyncClient(app=app, base_url="localhost:8000") as client:
            return client
