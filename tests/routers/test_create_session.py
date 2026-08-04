import pytest

from app.models import Session, SessionHandler
from app.dependencies.settings import get_settings

from tests.factories import (
    ManualSessionSubjectFactory,
    UrlSessionSubjectFactory,
    HSHSessionSubjectFactory,
    ManualHSHSessionSubjectFactory,
)


def test_create_session_manual_session(test_client, redis_client):
    user_input = ManualSessionSubjectFactory()
    input_json = user_input.dict()
    input_json["subject_type"] = input_json["subject_type"].value

    res = test_client.post("/session", data=input_json)
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
    input_json["subject_type"] = input_json["subject_type"].value

    res = test_client.post("/session", data=input_json)
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


def _all_task_dicts(tasks):
    for task in tasks:
        yield task
        yield from _all_task_dicts(task.get("children", {}).values())


def test_create_session_manual_hsh_session(test_client, redis_client):
    user_input = ManualHSHSessionSubjectFactory()
    input_json = user_input.dict()
    input_json["subject_type"] = input_json["subject_type"].value

    res = test_client.post("/session", data=input_json)
    assert res.status_code == 200

    session_data = res.json()
    assert session_data["tasks"] != {}

    for task in _all_task_dicts(session_data["tasks"].values()):
        assert task["name"].startswith("HSH")
        assert task["type"] == "task"


def test_create_session_hsh_manual_false_requires_metadata(test_client, redis_client):
    # Build a valid (non-manual) HSH subject, then strip metadata from the raw
    # payload to confirm the server-side validation still requires it when
    # is_manual is left at its default (False). Also a regression check for the
    # as_form decorator: a pydantic ValidationError raised while resolving the
    # `subject` Depends() used to escape as an uncaught 500 instead of a 422.
    user_input = HSHSessionSubjectFactory()
    input_json = user_input.dict()
    input_json["subject_type"] = input_json["subject_type"].value
    input_json.pop("metadata", None)
    input_json.pop("is_manual", None)

    res = test_client.post("/session", data=input_json)
    assert res.status_code == 422
    detail = res.json()["detail"]
    assert any(e["loc"] == ["subject_type"] for e in detail)


def test_create_session_url_requires_path(test_client, redis_client):
    # Same as_form decorator regression check as above, for the url branch.
    user_input = UrlSessionSubjectFactory()
    input_json = user_input.dict()
    input_json["subject_type"] = input_json["subject_type"].value
    input_json.pop("path", None)

    res = test_client.post("/session", data=input_json)
    assert res.status_code == 422
    detail = res.json()["detail"]
    assert any(e["loc"] == ["subject_type"] for e in detail)
