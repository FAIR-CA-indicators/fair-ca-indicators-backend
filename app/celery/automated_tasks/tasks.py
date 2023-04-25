import requests

from time import sleep
from app.celery.celery_app import app

from ... import routers, models

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
    print("Execution successfully called")
    sleep(10)
    session_id = task_dict["session_id"]
    task_id = task_dict["id"]

    if "id" in data:
        result = "success"
    else:
        result = "failed"

    status = models.TaskStatusIn(status=models.TaskStatus(result))

    print(f"Task status computed: {result}")
    requests.patch(f"http://localhost:8000/session/{session_id}/tasks/{task_id}", json=status.dict())

    # routers.update_task(session_id, task_id, status)  # Does not work because celery does not have access to fair_indicators
    # redis_app.json().set(f"session:{session_id}", f".tasks.{task_id}.status", obj=result)  # Works, but does not trigger updating of children
