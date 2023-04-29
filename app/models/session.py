from uuid import uuid4
from pydantic import BaseModel, HttpUrl, FileUrl, FilePath, validator
from typing import Union, Optional
from enum import Enum

from .tasks import (
    Task,
    TaskStatus,
    TaskPriority,
    Indicator,
    IndicatorDependency,
    DependencyType
)
from app.metrics.assessments_lifespan import fair_indicators
from app.dependencies.settings import get_settings


class SessionStatus(str, Enum):
    """
    List of statuses for a user session:

    - *queued*: The session object is created, but is not ready to run yet
    - *preprocessing*: The session is preparing the necessary information to run
    - *running*: Some of the Tasks associated with the session are not done
    - *postprocessing*: All Tasks are finished, and the session is cleaning up
    - *finished*: Everything is done
    - *error*: An error occurred while running
    """
    queued = "queued"
    preprocessing = "preprocessing"
    running = "running"
    postprocessing = "postprocessing"
    finished = "finished"
    error = "error"


class SubjectType(str, Enum):
    """
    Types of assessments queried by the user:
    - *url*: The archive/model to evaluate is at a specific url
    - *file*: The archive/model file is directly provided by the user
    - *manual*: No file is provided, the user will assess themselves the archive/model
    """
    url = "url"
    file = "file"
    manual = "manual"


class SessionSubjectIn(BaseModel):
    """
    Data input necessary to create a session object.

    - *path*: The PATH towards the resource (not required if *subject_type* is **manual**)
    - *has_archive*: Whether the assessed resource contains an archive (required attribute if *subject_type* is **manual**)
    - *has_model*: Whether the assessed resource contains a model (required attribute if *subject_type* is **manual**)
    - *has_archive_metadata*: Whether the assessed resource has metadata regarding the archive (required attribute if *subject_type* is **manual**)
    - *is_model_standard*: Whether the assessed model is in standard format (CellML, SBML, ...; required attribute if *subject_type* is **manual**)
    - *is_archive_standard*: Whether the assessed archive is in OMEX format (required attribute if *subject_type* is **manual**)
    - *is_model_metadata_standard*:
    - *is_archive_metadata_standard*: Whether the OMEX archive contains a manifest.xml file (required attribute if *subject_type* is **manual**)
    - *is_biomodel*: Whether the model comes from BioModel (required attribute if *subject_type* is **manual**)
    - *is_pmr*: Whether the model comes from PMR (required attribute if *subject_type* is **manual**)
    - *subject_type*: See SubjectType model
    """
    path: Union[HttpUrl, FileUrl, FilePath] = None
    has_archive: Optional[bool]
    has_model: Optional[bool]
    has_archive_metadata: Optional[bool]
    is_model_standard: Optional[bool]
    is_archive_standard: Optional[bool]
    is_model_metadata_standard: Optional[bool]
    is_archive_metadata_standard: Optional[bool]
    is_biomodel: Optional[bool]
    is_pmr: Optional[bool]
    subject_type: SubjectType

    @validator("subject_type", always=True)
    def necessary_data_provided(cls, subject_type: str, values: dict):
        if subject_type is SubjectType.manual:
            if (
                values.get("has_archive") is None
                or values.get("has_model") is None
                or values.get("has_archive_metadata") is None
                or values.get("is_model_standard") is None
                or values.get("is_archive_standard") is None
                or values.get("is_model_metadata_standard") is None
                or values.get("is_archive_metadata_standard") is None
                or values.get("is_pmr") is None
                or values.get("is_biomodel") is None
            ):
                raise ValueError("Self-assessments needs the form filled")
        else:
            if values.get("path") is None:
                raise ValueError("Url and file assessments need a url or path respectively")
        return subject_type



class Session(BaseModel):
    """
    A session object

    - *id*: The session identifier
    - *session_subject*: The user input used to create the session. See *SessionSubjectIn* model
    - *tasks*: Mapping of task identifiers to the corresponding Task object. Tasks with a parent are not included in
    this mapping (see Task model)
    - *status*: The session status (see SessionStatus model)
    - *score_all_essential*: Score based on all essential Tasks statuses
    - *score_all_non_essential*: Score based on all non-essential Tasks statuses
    - *score_all*: Score based on all Tasks statuses, including non-essential ones
    - *score_applicable_essential*: Identical to *score_all_essential*, excluding non-applicable Tasks
    - *score_applicable_nonessential*: Identical to *score_all_non_essential*, excluding non-applicable Tasks
    - *score_applicable_all*: Identical to *score_all*, excluding non-applicable Tasks
    - *ratio_not_applicable*: Percentage of assessments that do not apply to the evaluated resource
    """
    id: str
    session_subject: SessionSubjectIn
    tasks: dict[str, Task] = {}  # NEVER SET DIRECTLY, USE self.add_task()
    status: SessionStatus = SessionStatus.queued
    score_all_essential: float = 0
    score_all_nonessential: float = 0
    score_all: float = 0
    score_applicable_essential: float = 0
    score_applicable_nonessential: float = 0
    score_applicable_all: float = 0
    ratio_not_applicable: float = 0

    def get_task(self, task_id: str) -> Task:
        if task_id in self.tasks:
            return self.tasks[task_id]

        for task in self.tasks.values():
            tmp = task.get_task_child(task_id)
            if tmp is not None:
                return tmp

    def add_task(self, task: Task, parent_id: Optional[str] = None):
        if parent_id is not None:
            parent = self.get_task(parent_id)
            parent.add_task(task)
        else:
            self.tasks.update({task.id: task})

# TODO: Document methods
class SessionHandler:
    """
    The class to handle a session object. This class creates the task and their status
    based on user input, calculates the scores, ...
    """
    def __init__(self, session: Session) -> None:
        """
        Creates the handler based on a session. This session can already exist
        (see `from_existing_session`) or can be created using a SessionSubjectIn
        object (see `from_user_input`).

        :param session: The session object to handle
        """
        self.id = session.id
        self.user_input = session.session_subject
        self.session_model = session
        self.indicator_tasks = {}

        if not session.tasks:
            self.create_tasks()

        else:
            self._build_tasks_dict(list(self.session_model.tasks.values()))

    @classmethod
    def from_user_input(cls, session_data: SessionSubjectIn) -> "SessionHandler":
        """
        Creates a session based on user input (for example from the route `create_session`)
        and returns the handler for this session

        :param session_data:
        :return: A SessionHandler object
        """
        session = Session(id=str(uuid4()), session_subject=session_data)
        return cls(session)

    @classmethod
    def from_existing_session(cls, session: Session) -> "SessionHandler":
        """
        Creates a session handler for an existing session (for example loaded with the route
        `load_session`).

        :param session: A pre-existing session
        :return: A SessionHandler object
        """
        return cls(session)

    def _build_tasks_dict(self, tasks: list[Task]):
        """
        Creates the dictionary mapping all indicators names to their corresponding
        Task id in the Session object.

        :param tasks: List of Tasks in the session
        :return: None. The dict is directly stored in self
        """
        for task in tasks:
            # FIXME: Will fail when encountering task with multiple parent
            if task.name in self.indicator_tasks:
                raise ValueError(f"Multiple tasks with the same name ({task.name}) found")

            self.indicator_tasks.update({task.name: task.id})
            if task.children:
                self._build_tasks_dict(list(task.children.values()))

    def retrieve_metadata(self, url: str) -> None:
        """
        TODO: Method to retrieve the archive and models for url and file type assessments
        :param url:
        :return:
        """
        # See what is possible here
        pass

    # FIXME: Does not work. Does not take children into account
    #   We need to automatically update a session status once a task status is updated
    def is_running(self) -> bool:
        """Checks whether the session is still running or not"""
        return any([
            task.status is TaskStatus.queued
            or task.status is TaskStatus.started
            for task in self.session_model.tasks.values()
        ])

    def update_session_data(self):
        """
        Calculate the different statistics of the session (scores, non_applicable tasks ratio, ...)
        :return: None.
        """
        if not self.is_running():
            self.session_model.status = SessionStatus.finished

        all_tasks = [self.session_model.get_task(task_key) for task_key in self.indicator_tasks.values()]
        count_all_essential = 0
        count_all_nonessential = 0
        count_applicable_essential = 0
        count_applicable_nonessential = 0
        count_applicable_all = 0
        count_na = 0

        passed_all_essential = 0
        passed_all_nonessential = 0
        passed_all = 0
        passed_applicable_essential = 0
        passed_applicable_nonessential = 0
        passed_applicable_all = 0

        for task in all_tasks:
            passed_all += task.score

            if task.priority is not TaskPriority.essential:
                count_all_nonessential += 1
                passed_all_nonessential += task.score

                if task.status is not TaskStatus.not_applicable:
                    count_applicable_nonessential += 1
                    passed_applicable_nonessential += task.score
                    count_applicable_all += 1
                    passed_applicable_all += task.score

                else:
                    count_na += 1

            else:
                count_all_essential += 1
                passed_all_essential += task.score

                if task.status is not TaskStatus.not_applicable:
                    count_applicable_essential += 1
                    passed_applicable_essential += task.score
                    count_applicable_all += 1
                    passed_applicable_all += task.score

                else:
                    count_na += 1

        self.session_model.score_all = 0 if len(all_tasks) == 0 else passed_all / len(all_tasks)

        self.session_model.score_applicable_all = 0 \
            if count_applicable_all == 0 \
            else passed_applicable_all / count_applicable_all

        self.session_model.score_applicable_essential = 0 \
            if count_applicable_essential == 0 \
            else passed_applicable_essential / count_applicable_essential

        self.session_model.score_applicable_nonessential = 0 \
            if count_applicable_nonessential == 0 \
            else passed_applicable_nonessential / count_applicable_nonessential

        self.session_model.score_all_essential = 0 \
            if count_all_essential == 0 \
            else passed_all_essential / count_all_essential

        self.session_model.score_all_nonessential = 0 \
            if count_all_nonessential == 0 \
            else passed_all_nonessential / count_all_nonessential

        self.session_model.ratio_not_applicable = 0 \
            if len(all_tasks) == 0 \
            else count_na / len(all_tasks)

    def get_task_from_indicator(self, indicator: str):
        """Returns the Task in Session associated with an indicator"""
        return self.indicator_tasks[indicator] if indicator in self.indicator_tasks else None

    def create_tasks(self):
        """
        Creates all the tasks for the session based on existing fair_indicators
        (see `app.metrics.assessments_lifespan`)

        :return: None
        """
        for indicator in fair_indicators.values():
            # Skip if task for indicator is already created
            if indicator.name in self.indicator_tasks:
                continue

            task = self._create_task(indicator)
            self.indicator_tasks[indicator.name] = task.id

    def _get_default_task_status(self, indicator: str) -> tuple[TaskStatus, bool]:
        """
        Checks the status of an indicator dependencies (e.g. is the model from BioModel,
        is the assessment dependent on other Tasks, ...) and returns the default status
        for the Task associated with the given indicator.
        If the default status is automatically set or cannot be determined, for example
        if the depending Tasks are not finished, the Task associated with the given
        indicator is disabled.

        :param indicator: An indicator name
        :return: A tuple with the first element being the default status, the
        second being a boolean about whether the Task should be disabled or not
        """
        config = get_settings()
        if (
            indicator in config.archive_indicators
            and not self.user_input.has_archive
        ) or (
            indicator in config.archive_metadata_indicators
             and not self.user_input.has_archive_metadata
        ):
            return TaskStatus.failed, True

        if (
            indicator in config.biomodel_assessment_status
            and self.user_input.is_biomodel
        ):
            return TaskStatus(config.biomodel_assessment_status[indicator]), True

        if (
            indicator in config.pmr_indicator_status
            and self.user_input.is_pmr
        ):
            return TaskStatus(config.pmr_assessment_status[indicator]), True

        if indicator in config.assessment_dependencies:
            dependency_dict = config.assessment_dependencies[indicator]
            condition = DependencyType(dependency_dict.get("condition", "or"))

            dependency = IndicatorDependency(dependency_dict["indicators"], condition)
            parent_assessments = dependency.dependencies
            tasks = [self.session_model.get_task(self.get_task_from_indicator(a)) for a in parent_assessments]
            if dependency.is_automatically_failed(tasks):
                return TaskStatus.failed, True
            elif dependency.is_automatically_disabled(tasks):
                return TaskStatus.queued, True

        return TaskStatus.queued, False

    def _create_task(self, indicator: Indicator):
        """
        Create a task for a given indicator.
        If the task parents (the Tasks it depends on) do not exist, it recursively
        creates them.
        Also applies the default status to the created Task object.

        The task is stored either in the task parents `children` attribute or in
        the session_model `tasks` attribute.

        :param indicator: An indicator name
        :return: A Task object
        """
        task_id = str(uuid4())
        config = get_settings()

        task = Task(
            id=task_id,
            name=indicator.name,
            priority=TaskPriority(indicator.priority),
            session_id=self.id,
        )

        task_dependencies = config.assessment_dependencies.get(indicator.name)
        if task_dependencies is not None:
            for parent_indicator in task_dependencies["indicators"]:
                # If parent exists, no need to create it
                # FIXME: This will cause issues if a Task has multiple parents
                if parent_indicator in self.indicator_tasks:
                    parent_key = self.get_task_from_indicator(parent_indicator)
                    self.session_model.add_task(task, parent_key)

                else:
                    parent_task = self._create_task(parent_indicator)
                    self.indicator_tasks[parent_indicator] = parent_task.id
                    self.session_model.add_task(task, parent_task.id)

        else:
            self.session_model.add_task(task)

        default_status, default_disabled = self._get_default_task_status(indicator.name)
        task.status = default_status
        if default_status != TaskStatus.queued:
            task.automated = True
        task.disabled = default_disabled
        return task

    def update_task_children(self, task_key):
        """
        Update a Tasks children status.
        This method is called when a Task status is updated to propagate the change
        to its children

        :param task_key: The updated task id
        :return: None
        """
        task = self.session_model.get_task(task_key)
        for child in task.children.values():
            default_status, default_disabled = self._get_default_task_status(child.name)
            child.status = default_status
            child.disabled = default_disabled

    def json(self):
        """Returns the json representation of the session model"""
        return self.session_model.json()
