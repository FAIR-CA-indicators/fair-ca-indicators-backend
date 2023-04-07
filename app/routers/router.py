from fastapi import APIRouter, HTTPException
from typing import List
from redis.exceptions import ResponseError

from app.models.session import Session, SessionSubjectIn, SessionHandler, SubjectType
from app.models.tasks import Task, TaskStatusIn, Indicator
from app.metrics.assessments_lifespan import fair_indicators
from app.redis_controller import redis_app

base_router = APIRouter()



@base_router.post('/session', tags=["Sessions"])
def create_session(subject: SessionSubjectIn) -> Session:
    if subject.assessment_type is not SubjectType.manual:
        raise HTTPException(501, "The api only supports manual assessments at the moment")
    session_handler = SessionHandler(subject)
    session_handler.create_tasks()

    redis_app.json().set(f"session:{session_handler.session_model.id}", "$", obj=session_handler.session_model.dict())

    return session_handler.session_model


@base_router.post("/session/resume", tags=["Sessions"])
def load_session(session: Session) -> Session:
    existing_session_json = redis_app.json().get(f"session:{session.id}")
    if existing_session_json is not None:
        print(f"Impossible to create session from template, a session with if {session.id} already exists")
        subject = existing_session_json.pop("subject")
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
        subject = s_json.pop("subject")
        s = Session(**s_json, subject=subject)
        return s
    else:
        raise HTTPException(status_code=404, detail="No session with this id was found")


@base_router.get("/session/{session_id}/tasks/{task_id}", tags=["Tasks"])
def task_detail(session_id: str, task_id: str) -> Task:
    try:
        t_json = redis_app.json().get(f"session:{session_id}", f".tasks.{task_id}")
    except ResponseError:
        raise HTTPException(status_code=404,
                            detail="No task with this id was found")

    t = Task(**t_json)
    return t


@base_router.get("/indicators", tags=["Indicators"])
def indicator_descriptions_all() -> List[Indicator]:
    return list(fair_indicators.values())


@base_router.get("/indicators/{name}", tags=["Indicators"])
def indicator_description(name: str) -> Indicator:
    if name in fair_indicators:
        return fair_indicators[name]
    else:
        raise HTTPException(404, detail="No indicator with that name was found")


@base_router.patch("/session/{session_id}/tasks/{task_id}", tags=["Tasks"])
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

