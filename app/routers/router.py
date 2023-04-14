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
    if subject.subject_type is not SubjectType.manual:
        raise HTTPException(501, "The api only supports manual assessments at the moment")
    session_handler = SessionHandler.from_user_input(subject)

    redis_app.json().set(f"session:{session_handler.session_model.id}", "$", obj=session_handler.session_model.dict())

    return session_handler.session_model


@base_router.post("/session/resume", tags=["Sessions"])
def load_session(session: Session) -> Session:
    existing_session_json = redis_app.json().get(f"session:{session.id}")
    if existing_session_json is not None:
        print(f"Impossible to create session from template, a session with if {session.id} already exists")
        subject = existing_session_json.pop("session_subject")
        print(subject.path)
        existing_session = Session(**existing_session_json, session_subject=subject)
        if existing_session.session_subject.path == session.session_subject.path:
            print("Found session is identical to session sent by user")
            return existing_session
        else:
            raise HTTPException(409, "Existing session found for user-sent id")

    else:
        # TODO: Add checks regarding tasks and session status
        redis_app.json().set(f"session:{session.id}", "$", obj=session.dict())
        return session


@base_router.get("/session/{session_id}", tags=["Sessions"])
def session_details(session_id: str) -> Session:
    s_json = redis_app.json().get(f"session:{session_id}")
    if s_json is not None:
        subject = s_json.pop("session_subject")
        s = Session(**s_json, session_subject=subject)
        return s
    else:
        raise HTTPException(status_code=404, detail="No session with this id was found")


@base_router.get("/session/{session_id}/tasks/{task_id}", tags=["Tasks"])
def task_detail(session_id: str, task_id: str) -> Task:
    session = session_details(session_id)
    task = session.get_task(task_id)
    if task is not None:
        return task
    else:
        raise HTTPException(status_code=404,
                            detail="No task with this id was found")


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
def update_task(session_id: str, task_id: str, task_status: TaskStatusIn) -> Session:
    session = session_details(session_id)
    print(f"Session found: {session}")
    handler = SessionHandler.from_existing_session(session)

    task = handler.session_model.get_task(task_id)
    if task.disabled:
        raise HTTPException(status_code=403, detail="This task status was automatically set, changing its status is forbidden")
    task.status = task_status.status
    handler.update_task_children(task_id)

    try:
        redis_app.json().set(f"session:{session_id}", ".", handler.session_model.dict())
    except ResponseError:
        raise HTTPException(status_code=404,
                            detail="No task with this id was found")

    return handler.session_model

