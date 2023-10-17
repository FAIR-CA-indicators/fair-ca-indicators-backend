from app.models import SessionHandler
from tests.factories import SessionFactory


def test_route_session_details(test_client, redis_client):
    session = SessionFactory()
    redis_client.json().set(f"session:{session.id}", "$", obj=session.dict())

    res = test_client.get(f"/session/{session.id}")
    assert res.status_code == 200
    assert res.json() == session.dict()


def test_route_session_details_missing(test_client, redis_client):
    res = test_client.get("/session/random-session-id")
    assert res.status_code == 404


def test_route_task_details(test_client, redis_client):
    session = SessionFactory()
    sh = SessionHandler.from_existing_session(session)

    redis_client.json().set(f"session:{session.id}", "$", obj=session.dict())

    all_tasks = [
        sh.session_model.get_task(task_id) for task_id in sh.indicator_tasks.values()
    ]
    for task in all_tasks:
        res = test_client.get(f"/session/{session.id}/tasks/{task.id}")
        assert res.status_code == 200
        assert task.dict() == res.json()
