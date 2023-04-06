import os
from functools import lru_cache
from pydantic import BaseSettings
from typing import List, Mapping


class Config(BaseSettings):
    app_name: str = "FAIR Combine API"
    allowed_origins: List[str] = []
    assessment_dependencies: Mapping[str, dict] = {}


class DevConfig(Config):
    allowed_origins: List[str] = ["*"]
    pass


class ProdConfig(Config):
    pass


@lru_cache()
def get_settings():
    env = os.environ.get("FAIR_COMBINE_ENV", "dev")
    config = {"dev": DevConfig, "prod": ProdConfig}.get(env)()
    return config
