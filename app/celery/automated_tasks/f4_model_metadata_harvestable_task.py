import requests

from typing import Optional

from app.celery.celery_app import app
from app.dependencies.settings import get_settings
from ... import models


def dict_non_empty(metadata: dict):
    return any([bool(x) for x in metadata.values()])


@app.task
def f4_model_metadata_harvestable(
    task_dict: dict, data: dict, test: bool = False
) -> Optional["models.TaskStatus"]:
    """
    Representation of celery task to evaluate an assessment.
    These celery tasks should be in the format:
    ```
    def assessment_task(task_dict: dict, data: dict) -> None:
        session_id = task_dict["session_id"]
        task_id = task_dict["id"]

        # Code to get the final TaskStatus
        ...

        status = models.TaskStatusIn(status=models.TaskStatus(result), force_update=config.celery_key)
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

    if dict_non_empty(data["main_model_metadata"]):
        print(f"Found metadata: {data['main_model_metadata']}")
        result = "success"
    else:
        print("No metadata found")
        result = "failed"

    status = models.TaskStatusIn(
        status=models.TaskStatus(result), force_update=config.celery_key
    )

    print(f"Task status computed: {result}")
    if test:
        return models.TaskStatus(result)
    else:
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
