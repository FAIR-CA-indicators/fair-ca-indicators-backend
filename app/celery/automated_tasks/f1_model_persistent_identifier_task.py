import requests

from typing import Optional

from app.celery.celery_app import app
from app.dependencies.settings import get_settings
from urllib.parse import urlparse
from ... import models


def check_alt_ids(metadata: dict) -> bool:
    accepted_persistents = [
        "doi.org",
        "purl.org",
        "purl.oclc.org",
        "purl.net",
        "purl.com",
        "identifiers.org",
        "w3id.org",
    ]

    for resource_id in metadata["alt_ids"]:
        resource_url = urlparse(resource_id)
        if resource_url.netloc in accepted_persistents:
            return True

    return False


@app.task
def f1_model_persistent_identifier(
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
    try:
        if data["main_model_metadata"] and check_alt_ids(data["main_model_metadata"]):
            print("Found persistent identifiers in model metadata")
            result = "success"
        else:
            print("No persistent identifier was found for model")
            result = "failed"
    except Exception as e:
        print(f"An error occurred while assessing task: {str(e)}")
        result = "error"

    print(config.celery_key)
    status = models.TaskStatusIn(
        status=models.TaskStatus(result), force_update=config.celery_key
    )

    print(f"Task status computed: {result}")
    # Needs to send a request for the task to be updated
    if test:
        return models.TaskStatus(result)
    else:
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
