from redis import Redis
from redis.exceptions import ConnectionError
from threading import Lock

from app.dependencies.settings import get_settings


class RedisController(Redis):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.locks = {}

    # TODO: When redis deletes a session, we need to delete the corresponding lock
    def build_locks(self):
        session_keys = self.keys("session:*")
        for key in session_keys:
            try:
                session_id = key.split("session:")[1]
                self.locks[session_id] = Lock()
            except IndexError:
                raise ValueError(f"An unexpected key was found in redis: {key}")

    def add_lock(self, session_id: str):
        self.locks[session_id] = Lock()


def create_redis_app():
    config = get_settings()
    redis_app = RedisController(
        host=config.redis_url,
        port=config.redis_port,
        db=config.redis_db_number,
        # FIXME
        # username=os.environ.get("REDIS_USERNAME", "default"),
        # password=os.environ.get("REDIS_PASSWORD", "")
        decode_responses=True,
    )
    try:
        # Check that connection is working
        redis_app.ping()
        redis_app.build_locks()

    except ConnectionError as e:
        raise ConnectionError(f"An error occurred with redis server: {str(e)}")

    return redis_app


redis_app = create_redis_app()
