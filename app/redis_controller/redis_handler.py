import os

from redis import Redis
from redis.exceptions import ConnectionError



def create_redis_app():
    redis_app = Redis(
        host=os.environ.get("REDIS_URL", "localhost"),
        port=os.environ.get("REDIS_PORT", 6379),
        # FIXME
        # username=os.environ.get("REDIS_USERNAME", "default"),
        # password=os.environ.get("REDIS_PASSWORD", "")
        decode_responses=True,
    )
    try:
        # Check that connection is working
        redis_app.ping()
    except ConnectionError as e:
        raise ConnectionError(f"An error occurred with redis server: {str(e)}")
    # Loading dummy data for tests
    return redis_app


redis_app = create_redis_app()
