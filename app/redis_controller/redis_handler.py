import os

from pydantic import AnyUrl
from redis import Redis
from redis.exceptions import ConnectionError

from app.models.tasks import Task, TaskStatus
from app.models.session import Session


def create_redis_app():
    print("Connecting to redis cluster")
    redis_app = Redis(
        host=os.environ.get("REDIS_URL", "localhost"),
        port=os.environ.get("REDIS_PORT", 6379),
        # username=os.environ.get("REDIS_USERNAME", "default"),
        # password=os.environ.get("REDIS_PASSWORD", "")
        decode_responses=True,
    )
    try:
        print(redis_app.ping())
    except ConnectionError as e:
        raise ConnectionError(f"An error occurred with redis server: {str(e)}")
    # Loading dummy data for tests
    load_dummy_data(redis_app)
    return redis_app


def load_dummy_data(redis_app: "Redis"):
    dummy_session = Session(
        id="dummy-1234",
        subject=AnyUrl("http://test-url.com", scheme="http"),
        tasks={
            "12345-abcd": Task(
                id="12345-abcd",
                name="Dummy task",
                status=TaskStatus.queued,
                session_id="dummy-1234"
            ),
        }
    )
    redis_app.json().set(f"session:{dummy_session.id}", "$", obj=dummy_session.dict())

    # assert redis_app.get("foo") == "bar"
    pass


redis_app = create_redis_app()
