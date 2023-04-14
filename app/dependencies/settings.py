import os
from functools import lru_cache
from pydantic import BaseSettings
from typing import List

class Config(BaseSettings):
    app_name: str = "FAIR Combine API"
    allowed_origins: List[str] = []
    # List of indicators that applied to archive (if no archive, their statuses will be set to 'failed')
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

    # List of indicators that applied to archive metadata (if no archive, their statuses will be set to 'failed')
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

    # Mapping of indicators and their status that can be automatically set if data is stored in BioModel
    biomodel_assessment_status: dict[str, str] = {
        "CA-RDA-F1-01Archive": "failed",
        "CA-RDA-F1-01MA": "failed",
        "CA-RDA-A1-01MA": "not_applicable",
        "CA-RDA-A1-04Archive": "success",
        "CA-RDA-A1-04Model": "success",
        "CA-RDA-A1-04MA": "success",
        "CA-RDA-A1-05Model": "success",
        "CA-RDA-A1.1-01Model": "success",
        "CA-RDA-A1.1-01MA": "success",
        "CA-RDA-A1.2-01Archive": "success",
        "CA-RDA-A1.2-01Model": "success",
        "CA-RDA-R1.1-01MA": "success",
        "CA-RDA-R1.1-01MM": "success",
        "CA-RDA-R1.1-02MM": "success",
        "CA-RDA-R1.1-03MM": "success",
    }

    # Mapping of indicators and their status that can be automatically set if data is stored in PMR
    pmr_indicator_status: dict[str, str] = {}

    # Mapping of indicators with their direct parent. Until parent status is 'success', children cannot be set.
    # Not happy with this, as it means that the Config is dynamically set
    assessment_dependencies: dict[str, dict] = {
        "CA-RDA-I3-02Archive": {"condition": "or", "indicators": ["CA-RDA-I3-01Archive"]},
        "CA-RDA-I3-02Model": {"condition": "or", "indicators": ["CA-RDA-I3-01Model"]},
        "CA-RDA-I3-03MA": {"condition": "or", "indicators": ["CA-RDA-I3-01MA"]},
        "CA-RDA-I3-03MM": {"condition": "or", "indicators": ["CA-RDA-I3-01MM"]},
        "CA-RDA-I3-04MA": {"condition": "or", "indicators": ["CA-RDA-I3-02MA"]},
        "CA-RDA-I3-04MM": {"condition": "or", "indicators": ["CA-RDA-I3-02MM"]},
        "CA-RDA-R1.1-02MA": {"condition": "or", "indicators": ["CA-RDA-R1.1-01MA"]},
        "CA-RDA-R1.1-03MA": {"condition": "or", "indicators": ["CA-RDA-R1.1-01MA"]},
    }


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
