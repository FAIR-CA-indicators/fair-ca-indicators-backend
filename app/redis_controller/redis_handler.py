import os

from pydantic import HttpUrl
from redis import Redis
from redis.exceptions import ConnectionError

import app.models as models

def create_redis_app():
    print("Connecting to redis cluster")
    redis_app = Redis(
        host=os.environ.get("REDIS_URL", "localhost"),
        port=os.environ.get("REDIS_PORT", 6379),
        # FIXME
        # username=os.environ.get("REDIS_USERNAME", "default"),
        # password=os.environ.get("REDIS_PASSWORD", "")
        decode_responses=True,
    )
    try:
        print(redis_app.ping())
    except ConnectionError as e:
        raise ConnectionError(f"An error occurred with redis server: {str(e)}")
    # Loading dummy data for tests
    return redis_app


def load_dummy_data(redis_app: "Redis"):
    dummy_session = models.Session(
        id="dummy-1234",
        session_subject=models.SessionSubjectIn(
            subject_type=models.SubjectType("url"),
            path=HttpUrl("http://test.com", scheme="http"),
        ),
        tasks={
            "12345-abcd": models.Task(
                id="12345-abcd",
                name="CA-RDA-F1-01Archive",
                status=models.TaskStatus.queued,
                session_id="dummy-1234"
            ),
        }
    )
    redis_app.json().set(f"session:{dummy_session.id}", "$", obj=dummy_session.dict())


redis_app = create_redis_app()
