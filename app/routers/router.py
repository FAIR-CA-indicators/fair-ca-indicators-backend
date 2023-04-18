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
    """
    Create a new session based on user input

    **Parameters:**

    - *subject*: Pydantic model containing user input.

    **Returns:**
    The created session
    \f
    :param subject: Pydantic model containing user input.
    :return: The created session
    """
    if subject.subject_type is not SubjectType.manual:
        raise HTTPException(501, "The api only supports manual assessments at the moment")
    session_handler = SessionHandler.from_user_input(subject)

    redis_app.json().set(f"session:{session_handler.session_model.id}", "$", obj=session_handler.session_model.dict())

    return session_handler.session_model


@base_router.post("/session/resume", tags=["Sessions"])
def load_session(session: Session) -> Session:
    """
    Load a session based on JSON previously downloaded by user

    **Parameters:**

    - *session*: A JSON object representing a Session.

    **Returns:**
    The loaded session
    \f
    :param session: Pydantic model to convert the JSON downloaded by user into
        a working session object

    :return: The loaded session
    """
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
    """
    Returns the details about an existing session

    **Parameters:**

    - *session_id*: A session identifier

    **Returns:**
    The session object corresponding to the given id
    \f
    :param session_id: The session identifier
    :return: The session object corresponding to the given id
    """
    s_json = redis_app.json().get(f"session:{session_id}")
    if s_json is not None:
        subject = s_json.pop("session_subject")
        s = Session(**s_json, session_subject=subject)
        return s
    else:
        raise HTTPException(status_code=404, detail="No session with this id was found")


@base_router.get("/session/{session_id}/tasks/{task_id}", tags=["Tasks"])
def task_detail(session_id: str, task_id: str) -> Task:
    """
    Returns the information about a specific Task

    **Parameters:**

    - *session_id*: A session identifier
    - *task_id*: A task identifier

    **Returns:**
    The Task associated with the given identifier
    \f
    :param session_id: The id of the session the Task is associated with
    :param task_id: The identifier of the wanted Task
    :return: The Task associated with the given identifier
    """
    session = session_details(session_id)
    task = session.get_task(task_id)
    if task is not None:
        return task
    else:
        raise HTTPException(status_code=404,
                            detail="No task with this id was found")


@base_router.get("/indicators", tags=["Indicators"])
def indicator_descriptions_all() -> List[Indicator]:
    """
    Returns all the FAIR assessments evaluated in FAIR Combine

    **Returns:**

    The list of all FAIR Combine assessment indicators
    \f
    :return: A list of Indicator
    """
    return list(fair_indicators.values())


@base_router.get("/indicators/{name}", tags=["Indicators"])
def indicator_description(name: str) -> Indicator:
    """
    Returns a specific FAIR assessments indicator

    **Parameters:**

    - *name*: A FAIR Combine assessment name (e.g. CA-RDA-F1-01Archive)

    **Returns:**
    The Indicator associated with the given name
    \f
    :param name: The name of an Indicator
    :return: The Indicator associated with the given name
    """
    if name in fair_indicators:
        return fair_indicators[name]
    else:
        raise HTTPException(404, detail="No indicator with that name was found")


@base_router.patch("/session/{session_id}/tasks/{task_id}", tags=["Tasks"])
def update_task(session_id: str, task_id: str, task_status: TaskStatusIn) -> Session:
    """
    Edit the status of a Task to the given TaskStatus and recalculate the
    default status for the children of that Task

    **Parameters:**

    - *session_id*: The id of the session the Task is associated with
    - *task_id*: The identifier of the wanted Task
    - *task_status*: The new TaskStatus

    **Returns:**
    The session with the updated Tasks
    \f
    :param session_id: The id of the session the Task is associated with
    :param task_id: The identifier of the wanted Task
    :param task_status: The new TaskStatus
    :return: The whole session.
    """
    session = session_details(session_id)
    handler = SessionHandler.from_existing_session(session)

    task = handler.session_model.get_task(task_id)
    if task.disabled:
        raise HTTPException(status_code=403, detail="This task status was automatically set, changing its status is forbidden")
    task.status = task_status.status
    handler.update_task_children(task_id)
    handler.run_statistics()

    try:
        redis_app.json().set(f"session:{session_id}", ".", handler.session_model.dict())
    except ResponseError:
        raise HTTPException(status_code=404,
                            detail="No task with this id was found")

    return handler.session_model

