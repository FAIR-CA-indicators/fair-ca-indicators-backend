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
    queued = "queued"
    preprocessing = "preprocessing"
    running = "running"
    postprocessing = "postprocessing"
    finished = "finished"
    error = "error"


class SubjectType(str, Enum):
    url = "url"
    file = "file"
    manual = "manual"


class SessionSubjectIn(BaseModel):
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
    id: str
    session_subject: SessionSubjectIn
    tasks: dict[str, Task] = {}
    status: SessionStatus = SessionStatus.queued
    score_all_essential: Optional[float]
    score_all_nonessential: Optional[float]
    score_all: Optional[float]
    score_applicable_essential: Optional[float]
    score_applicable_nonessential: Optional[float]
    score_applicable_all: Optional[float]

    def get_task(self, task_id: str) -> Task:
        if task_id in self.tasks:
            return self.tasks[task_id]

        for task in self.tasks.values():
            tmp = task.get_task_child(task_id)
            if tmp is not None:
                return tmp

# TODO: Document methods
class SessionHandler:
    def __init__(self, session: Session) -> None:
        self.id = session.id
        self.user_input = session.session_subject
        self.session_model = session
        self.indicator_tasks = {}

        if not session.tasks:
            self.create_tasks()

        else:
            self.build_tasks_dict(list(self.session_model.tasks.values()))
        # self.id: str = str(uuid4())
        #
        # self.user_input: SessionSubjectIn = session_data
        # self.session_model: Session = Session(id=self.id, subject=session_data.path)
        # self.indicator_tasks: dict[str, str] = {}
        #
        # # Create the tasks for all indicators and set their default statuses
        # self.create_tasks()
        #
        # self.metadata = {}
        # self.retrieve_metadata(self.session_model.subject)

    @classmethod
    def from_user_input(cls, session_data: SessionSubjectIn) -> "SessionHandler":
        session = Session(id=str(uuid4()), session_subject=session_data)
        return cls(session)

    @classmethod
    def from_existing_session(cls, session: Session) -> "SessionHandler":
        return cls(session)

    def build_tasks_dict(self, tasks: list[Task]):
        for task in tasks:
            if task.name in self.indicator_tasks:
                raise ValueError(f"Multiple tasks with the same name ({task.name}) found")

            self.indicator_tasks.update({task.name: task.id})
            if task.children:
                self.build_tasks_dict(list(task.children.values()))

    def retrieve_metadata(self, url: str) -> None:
        # See what is possible here
        pass

    def is_running(self) -> bool:
        """Checks whether the session is still running or not"""
        return any([task.status is TaskStatus.queued or task.status is TaskStatus.started for task in self.session_model.tasks.values()])

    def run_statistics(self):
        if self.is_running():
            return
        else:
            self._calculate_score_essential()
            self._calculate_score_all()
            self._calculate_na_ratio()

    def _count_essential(self):
        # TODO: Correct this
        return sum([t.priority is TaskPriority.essential and t.status is not TaskStatus.not_applicable for t in self.session_model.tasks.values()])

    def _count_applicable(self):
        # TODO: Correct this
        return sum([t.status is not TaskStatus.not_applicable for t in self.session_model.tasks.values()])

    def _calculate_na_ratio(self):
        # TODO: Correct this
        self.session_model.ratio_not_applicable = sum([t.status is TaskStatus.not_applicable for t in self.session_model.tasks.values()]) / len(self.session_model.tasks)

    def _calculate_score_essential(self):
        # TODO: Correct this
        self.session_model.score_essential = sum([
            t.score for t in self.session_model.tasks.values() if t.priority is TaskPriority.essential and t.status is not TaskStatus.not_applicable
        ]) / self._count_essential()

    def _calculate_score_all(self):
        # TODO: Correct this
        self.session_model.score_all = sum([t.score for t in self.session_model.tasks.values() if t.status is not TaskStatus.not_applicable]) / self._count_applicable()

    def get_task_from_indicator(self, indicator: str):
        """Returns the Task in Session associated with an indicator"""
        return self.indicator_tasks[indicator] if indicator in self.indicator_tasks else None

    # TODO: Test that this work even if children are created before parents
    # TODO: Test that the default statuses are correctly set
    def create_tasks(self):
        for indicator in fair_indicators.values():
            # Skip if task for indicator is already created
            if indicator.name in self.indicator_tasks:
                continue

            key, task, = self._create_task(indicator)
            self.indicator_tasks[indicator.name] = key

    def _get_default_task_status(self, indicator: str) -> tuple[TaskStatus, bool]:
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
                if parent_indicator in self.indicator_tasks:
                    parent_key = self.get_task_from_indicator(parent_indicator)
                    parent_task = self.session_model.get_task(parent_key)
                    parent_task.children[task_id] = task
                    # task.parents[parent_key] = parent_task

                else:
                    key, parent_task = self._create_task(parent_indicator)
                    self.indicator_tasks[parent_indicator] = key
                    parent_task.children[task_id] = task

                    # task.parents[key] = parent_task

        else:
            self.session_model.tasks[task_id] = task

        default_status, default_disabled = self._get_default_task_status(indicator.name)
        task.status = default_status
        task.disabled = default_disabled
        return task_id, task

    def update_task_children(self, task_key):
        task = self.session_model.get_task(task_key)
        for child in task.children.values():
            default_status, default_disabled = self._get_default_task_status(child.name)
            child.status = default_status
            child.disabled = default_disabled

    def json(self):
        """Returns the json representation of the session model"""
        return self.session_model.json()
