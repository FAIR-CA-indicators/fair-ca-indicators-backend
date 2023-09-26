import uuid

import pytest

from app.models import SessionHandler, Session, TaskStatus
from app.dependencies.settings import get_settings
from tests.factories import ManualSessionSubjectFactory


@pytest.mark.parametrize("force_update", [True, False])
def test_update_disabled_task(test_client, redis_client, force_update):
    config = get_settings()
    user_input = ManualSessionSubjectFactory()
    id = "test-session"
    session_handler = SessionHandler.from_user_input(id, user_input)

    disabled_task = list(session_handler.session_model.tasks.values())[0]
    disabled_task.disabled = True

    redis_client.json().set(
        f"session:{session_handler.id}", "$", session_handler.dict()
    )

    if force_update:
        response = test_client.patch(
            f"/session/{session_handler.id}/tasks/{disabled_task.id}",
            json={"status": "success", "force_update": config.celery_key},
        )
        assert response.status_code == 200
        updated_task = redis_client.json().get(
            f"session:{session_handler.id}", f".tasks.{disabled_task.id}"
        )

        assert updated_task["status"] == TaskStatus.success

    else:
        response = test_client.patch(
            f"/session/{session_handler.id}/tasks/{disabled_task.id}",
            json={"status": "success"},
        )
        assert response.status_code == 403
        updated_task = redis_client.json().get(
            f"session:{session_handler.id}", f".tasks.{disabled_task.id}"
        )

        assert updated_task["status"] == TaskStatus.queued


@pytest.mark.parametrize(
    "status",
    [
        TaskStatus.queued,
        TaskStatus.started,
        TaskStatus.not_applicable,
        TaskStatus.not_answered,
        TaskStatus.success,
        TaskStatus.failed,
        TaskStatus.warnings,
        TaskStatus.error,
    ],
)
def test_update_task(status, test_client, redis_client):
    user_input = ManualSessionSubjectFactory()
    id = str(uuid.uuid4())
    session_handler = SessionHandler.from_user_input(id, user_input)

    task = [
        t for t in session_handler.session_model.tasks.values() if t.children != {}
    ][0]
    assert task is not None
    assert task.status == TaskStatus.queued

    redis_client.json().set(
        f"session:{session_handler.id}", ".", session_handler.dict()
    )

    # Check that request worked
    response = test_client.patch(
        f"/session/{session_handler.id}/tasks/{task.id}", json={"status": status.value}
    )
    assert response.status_code == 200

    updated_session_json = redis_client.json().get(f"session:{session_handler.id}", ".")
    updated_session = Session(**updated_session_json)

    # Check that task status has changed in Redis
    updated_task = updated_session.get_task(task.id)
    assert updated_task.status == status

    # Check that session score has changed (if valid)
    # FIXME: Should be set in settings!
    score_offset = {
        TaskStatus.success: 1,
        TaskStatus.failed: 0,
        TaskStatus.warnings: 0.5,
    }.get(status, 0)

    assert updated_session.score_all == (
        session_handler.session_model.score_all + score_offset
    ) / len(session_handler.indicator_tasks.values())

    print(updated_task)
    # Check that task children are updated
    if status in [TaskStatus.failed, TaskStatus.queued, TaskStatus.started]:
        assert all([t.disabled for t in updated_task.children.values()])

    elif status in [
        TaskStatus.error,
        TaskStatus.success,
        TaskStatus.not_applicable,
        TaskStatus.not_answered,
        TaskStatus.warnings,
    ]:
        assert all([not t.disabled for t in updated_task.children.values()])

    else:
        raise AssertionError(
            f"Forgot to test disabled status of task children when task status is {status}"
        )
