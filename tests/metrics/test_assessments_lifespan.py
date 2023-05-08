import pytest
import logging

from csv import DictReader

from app.metrics.assessments_lifespan import fair_indicators
from app.dependencies.settings import get_settings


logger = logging.getLogger(__name__)


# Needed to be marked like this because only asyncclients get the fair_indicators loaded
@pytest.mark.anyio
async def test_fair_indicators(test_asyncclient):
    assert fair_indicators != {}
    config = get_settings()

    with open(config.indicators_path, "r") as file_handler:
        csv_reader = DictReader(file_handler, dialect="unix")

        for line in csv_reader:
            assert line["TaskName"] in fair_indicators
