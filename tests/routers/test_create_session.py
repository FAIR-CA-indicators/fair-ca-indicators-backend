from app.models import Session


def test_create_session_manual_session(test_client, redis_client):
    input_form = {
        "subject_type": "manual",
        "has_archive": True,
        "has_model": True,
        "has_archive_metadata": True,
        "is_model_standard": False,
        "is_archive_standard": False,
        "is_model_metadata_standard": False,
        "is_archive_metadata_standard": False,
        "is_biomodel": False,
        "is_pmr": False,
    }

    res = test_client.post("/session", json=input_form)
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


def test_create_biomodel_session(test_client):
    pass


def test_create_pmr_session(test_client):
    pass
