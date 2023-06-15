import pytest

from app.models import Session
from tests.factories import ManualSessionSubjectFactory, SessionFactory


@pytest.mark.parametrize("existing", [True, False])
def test_load_session(existing, test_client, redis_client):
    if existing:
        user_input = ManualSessionSubjectFactory()
        session = SessionFactory(session_subject=user_input)
        redis_client.json().set(f"session:{session.id}", "$", obj=session.dict())

    else:
        session = SessionFactory()

    res = test_client.post("/session/resume", json=session.dict())
    assert res.status_code == 200

    resumed_json = redis_client.json().get(f"session:{session.id}")
    assert resumed_json == res.json()
    resumed_session = Session(**res.json())
    if existing:
        assert resumed_session.session_subject == session.session_subject
