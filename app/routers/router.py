import uuid
import os
from shutil import copyfileobj
from fastapi import APIRouter, HTTPException, UploadFile, Depends
from typing import List, Optional
from redis.exceptions import ResponseError


from app.models import (
    Session,
    SessionSubjectIn,
    SessionHandler,
    SubjectType,
    Task,
    AutomatedTask,
    TaskStatusIn,
    Indicator,
)
from app.metrics.assessments_lifespan import fair_indicators
from app.redis_controller import redis_app
from app.dependencies.settings import get_settings

base_router = APIRouter()

@base_router.post("/session", tags=["Sessions"])
def create_session(
    subject: SessionSubjectIn = Depends(SessionSubjectIn.as_form),
    uploaded_file: Optional[UploadFile] = None,
    metadata: Optional[object] = None
) -> Session:
    """
    Create a new session based on user input

    **Parameters:**

    - *subject*: Pydantic model containing user input.

    **Returns:**
    The created session
    \f
    :param subject: Pydantic model containing user input.
    :param uploaded_file: If subject type is 'file', this contains the uploaded omex archive.
    :param metadata: If subject is "metadata" this object contains metadata from the CSH
    :return: The created session
    """
    session_id = str(uuid.uuid4())

    print("created session " + session_id)


    if subject.subject_type is SubjectType.url:
        raise HTTPException(
            501, "The api only supports manual assessments at the moment"
        )
    elif subject.subject_type is SubjectType.file:
        if uploaded_file is None:
            raise HTTPException(
                422, "No file was uploaded for assessment. Impossible to process query"
            )

        # Loading file
        try:
            # This is wrong path, file should be moved to the session directory
            path = f"./session_files/{session_id}/{uploaded_file.filename}"
            os.makedirs(f"./session_files/{session_id}")
            with open(path, "wb") as buffer:
                copyfileobj(uploaded_file.file, buffer)
            subject.path = path
        finally:
            uploaded_file.file.close()
    elif subject.subject_type is SubjectType.csh:
        if subject.metadata is None:
            raise HTTPException(
                422, "No JSON object was attached for assessment. Impossible to process query"
            )
    try:
        session_handler = SessionHandler.from_user_input(session_id, subject) 
    except ValueError as e:
        raise HTTPException(422, str(e))
    try:
        redis_app.json().set(
            f"session:{session_handler.session_model.id}",
            "$",
            obj=session_handler.session_model.dict(),
        )
        session_handler.start_automated_tasks()
    except TypeError as e:
        print(session_handler.session_model)
        print(session_handler.session_model.dict())
        raise e

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
        subject = existing_session_json.pop("session_subject")
        existing_session = Session(**existing_session_json, session_subject=subject)
        if existing_session.session_subject == session.session_subject:
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
        raise HTTPException(status_code=404, detail="No task with this id was found")


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
async def update_task(
    session_id: str, task_id: str, task_status: TaskStatusIn
) -> Session:
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
    :param force: Force the task status update even if task is disabled
    :return: The whole session.
    """
    config = get_settings()
    redis_app.locks[session_id].acquire(timeout=60)

    session = session_details(session_id)
    handler = SessionHandler.from_existing_session(session)

    task = handler.session_model.get_task(task_id)

    if task.disabled and task_status.force_update != config.celery_key:
        print(
            f"Wrong key given ({task_status.force_update}). Expected {config.celery_key}"
        )
        redis_app.locks[session_id].release()
        raise HTTPException(
            status_code=403,
            detail="This task status was automatically set, changing its status is forbidden",
        )

    # If query is not sent by celery, set the task as non-automated
    if task_status.force_update != config.celery_key:
        task.automated = False
    # If AutomatedTask is updated by celery, it means the assessment is done and task can be enabled
    if task_status.force_update == config.celery_key and isinstance(
        task, AutomatedTask
    ):
        task.disabled = False
    task.status = task_status.status

    handler.update_task_children(task_id)
    handler.update_session_data()

    try:
        redis_app.json().set(f"session:{session_id}", ".", handler.session_model.dict())
    except ResponseError as e:
        print(f"An error occurred in Redis: {str(e)}")
        raise HTTPException(status_code=404, detail="No task with this id was found")
    finally:
        redis_app.locks[session_id].release()

    return handler.session_model
