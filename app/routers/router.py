from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import AnyUrl
from typing import List
from redis.exceptions import ResponseError

from app.models.session import Session, SessionSubjectIn
from app.models.tasks import Task, TaskStatusIn, TaskDescription
from app.metrics.assessments_lifespan import fair_assessments
from app.redis_controller import redis_app

base_router = APIRouter()


def create_tasks():
    return {}


@base_router.post('/session/create', tags=["Sessions"])
def create_session(subject: SessionSubjectIn) -> Session:
    session_id = str(uuid4())
    session = Session(id=session_id, subject=subject.path)
    session.tasks = create_tasks()

    redis_app.json().set(f"session:{session.id}", "$", obj=session.dict())

    return session


@base_router.post("/session/load", tags=["Sessions"])
def load_session(session: Session) -> Session:
    existing_session_json = redis_app.json().get(f"session:{session.id}")
    if existing_session_json is not None:
        print(f"Impossible to create session from template, a session with if {session.id} already exists")
        subject = AnyUrl(existing_session_json.pop("subject"), scheme="http")
        print(subject)
        existing_session = Session(**existing_session_json, subject=subject)
        if existing_session.subject == session.subject:
            print("Found session is identical to session sent by user")
            return existing_session
        else:
            raise HTTPException(409, "Existing session found for user-sent id")

    else:
        redis_app.json().set(f"session:{session.id}", "$", obj=session.dict())
        return session


@base_router.get("/session/{session_id}", tags=["Sessions"])
def session_details(session_id: str) -> Session:
    s_json = redis_app.json().get(f"session:{session_id}")
    if s_json is not None:
        subject = AnyUrl(s_json.pop("subject"), scheme="http")
        s = Session(**s_json, subject=subject)
        return s
    else:
        raise HTTPException(status_code=404, detail="No session with this id was found")


@base_router.get("/session/{session_id}/tasks/{task_id}", tags=["Assessments"])
def task_detail(session_id: str, task_id: str) -> Task:
    try:
        t_json = redis_app.json().get(f"session:{session_id}", f".tasks.{task_id}")
    except ResponseError:
        raise HTTPException(status_code=404,
                            detail="No task with this id was found")

    t = Task(**t_json)
    return t



@base_router.get("/about_tasks", tags=["Assessments"])
def task_descriptions_all() -> List[TaskDescription]:
    return list(fair_assessments.values())


@base_router.get("/about_tasks/{task_name}", tags=["Assessments"])
def task_description(task_name) -> TaskDescription:
    if task_name in fair_assessments:
        return fair_assessments[task_name]
    else:
        raise HTTPException(404, detail="No task with that name was found")


@base_router.post("/session/{session_id}/tasks/{task_id}/edit", tags=["Assessments"])
def update_task(session_id: str, task_id: str, task_status: TaskStatusIn) -> Task:
    try:
        redis_app.json().set(f"session:{session_id}", f".tasks.{task_id}.status", task_status.status)
        task_json = redis_app.json().get(f"session:{session_id}", f".tasks.{task_id}")
    except ResponseError:
        raise HTTPException(status_code=404,
                            detail="No task with this id was found")

    return Task(**task_json)
    # Need to check that this is not an automated task!
    # return Task(session_id=session_id, id=task_id, name="Updated Dummy task", status=task_status)

