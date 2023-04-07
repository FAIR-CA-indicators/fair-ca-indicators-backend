import os
from functools import lru_cache
from pydantic import BaseSettings
from typing import List


class Config(BaseSettings):
    app_name: str = "FAIR Combine API"
    allowed_origins: List[str] = []
    archive_indicators: List[str] = [
        "CA-RDA-F1-01Archive",
        "CA-RDA-F1-02Archive",
        "CA-RDA-A1-02Archive",
        "CA-RDA-A1-03Archive",
        "CA-RDA-A1-04Archive",
        "CA-RDA-A1-05Archive",
        "CA-RDA-A1.1-01Archive",
        "CA-RDA-A1.2-01Archive",
        "CA-RDA-I1-01Archive",
        "CA-RDA-I1-02Archive",
        "CA-RDA-I2-01Archive",
        "CA-RDA-I3-01Archive",
        "CA-RDA-I3-02Archive",
        "CA-RDA-R1.3-01Archive",
        "CA-RDA-R1.3-02Archive",
    ]
    archive_metadata_indicators: List[str] = [
        "CA-RDA-F1-01MA",
        "CA-RDA-F1-02MA",
        "CA-RDA-F2-01MA",
        "CA-RDA-F3-01MA",
        "CA-RDA-F4-01MA",
        "CA-RDA-A1-01MA",
        "CA-RDA-A1-02MA",
        "CA-RDA-A1-03MA",
        "CA-RDA-A1-04MA",
        "CA-RDA-A1.1-01MA",
        "CA-RDA-A2-01MA",
        "CA-RDA-I1-01MA",
        "CA-RDA-I1-02MA",
        "CA-RDA-I2-01MA",
        "CA-RDA-I3-01MA",
        "CA-RDA-I3-02MA",
        "CA-RDA-I3-03MA",
        "CA-RDA-I3-04MA",
        "CA-RDA-R1-01MA",
        "CA-RDA-R1.1-01MA",
        "CA-RDA-R1.1-02MA",
        "CA-RDA-R1.1-03MA",
        "CA-RDA-R1.2-01MA",
        "CA-RDA-R1.2-02MA",
        "CA-RDA-R1.3-01MA",
        "CA-RDA-R1.3-02MA",
        "CA-RDA-R1.3-03MA",
    ]
    assessment_dependencies: dict[str, list] = {}


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
