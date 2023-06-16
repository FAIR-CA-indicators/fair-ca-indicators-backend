import requests

from app.celery.celery_app import app
from app.dependencies.settings import get_settings
from ... import models


@app.task
def f1_model_persistent_identifier(task_dict: dict, data: dict) -> None:
    """
    Representation of celery task to evaluate an assessment.
    These celery tasks should be in the format:
    ```
    def assessment_task(task_dict: dict, data: dict) -> None:
        session_id = task_dict["session_id"]
        task_id = task_dict["id"]

        # Code to get the final TaskStatus
        result = evaluate_assessment(data)

        status = models.TaskStatusIn(status=models.TaskStatus(result))
        requests.patch(
            f"http://localhost:8000/session/{session_id}/tasks/{task_id},
            json=status
        )

    :param task_dict: Task dict representation
    :param data: (Meta)Data to evaluate
    :return: None
    """
    config = get_settings()
    print("Execution successfully called")
    session_id = task_dict["session_id"]
    task_id = task_dict["id"]

    if data["main_model_object"].get("id"):
        print(f"Found model id {data['main_model_object'].get('id')}")
        result = "success"
    else:
        print("No id was found in model")
        result = "failed"

    status = models.TaskStatusIn(status=models.TaskStatus(result))

    print(f"Task status computed: {result}")
    # Needs to send a request for the task to be updated
    url = f"http://{config.backend_url}:{config.backend_port}/session/{session_id}/tasks/{task_id}"
    print(f"Patching {url}")
    requests.patch(
        url,
        json=status.dict(),
    )

    # Does not work because celery does not have access to fair_indicators
    # routers.update_task(session_id, task_id, status)

    # Works, but does not trigger updating of children
    # redis_app.json().set(f"session:{session_id}", f".tasks.{task_id}.status", obj=result)
