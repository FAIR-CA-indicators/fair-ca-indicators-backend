import pytest

from app.models import Session, SessionHandler
from app.dependencies.settings import get_settings

from tests.factories import ManualSessionSubjectFactory


def test_create_session_manual_session(test_client, redis_client):
    user_input = ManualSessionSubjectFactory()
    input_json = user_input.dict()

    res = test_client.post("/session", json=input_json)
    assert res.status_code == 200
    session_data = res.json()
    # FIXME: Is there a way to get redis running in test env?
    # stored_data = redis_app.json().get(session_data["id"])
    # assert stored_data is not None
    s = Session(**session_data)
    assert s.tasks != []
    assert s.status == "queued"
    assert s.score_all == 0
    assert s.score_all_essential == 0
    assert s.score_all_nonessential == 0
    assert s.score_applicable_all == 0
    assert s.score_applicable_nonessential == 0
    assert s.score_applicable_essential == 0


@pytest.mark.parametrize("repo", ["biomodel", "pmr"])
def test_create_repository_based_session(repo, test_client, redis_client):
    config = get_settings()
    user_input = {
        "biomodel": ManualSessionSubjectFactory(is_biomodel=True),
        "pmr": ManualSessionSubjectFactory(is_pmr=True),
    }[repo]

    input_json = user_input.dict()

    res = test_client.post("/session", json=input_json)
    assert res.status_code == 200

    s = Session(**res.json())
    sh = SessionHandler.from_existing_session(s)

    dependencies = {
        "biomodel": config.biomodel_assessment_status,
        "pmr": config.pmr_indicator_status,
    }[repo]

    for indicator, expected_status in dependencies.items():
        task_key = sh.get_task_from_indicator(indicator)
        task = s.get_task(task_key)

        assert task.status == expected_status
