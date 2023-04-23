import celery.exceptions
from celery import Celery
from typing import TYPE_CHECKING
from time import sleep

if TYPE_CHECKING:
    from app.models import AutomatedTask, SessionSubjectIn

#FIXME Need to load broker from settings
app = Celery("fair-combine", broker="redis://localhost:6379/0")

@app.task
def hello_world():
    return "Hello world!"


@app.task
def execute_task(**kwargs):
    task = kwargs.pop("task")
    data = kwargs.pop("data")
    if task is None or data is None:
        raise celery.exceptions.TaskError("Task was called without the expected arguments")

    print("Execution successfully called")
    sleep(10)
    evaluation_status = task.evaluate(data)

    return evaluation_status