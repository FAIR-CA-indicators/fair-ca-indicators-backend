from uuid import uuid4
from pydantic import BaseModel, HttpUrl, FileUrl, FilePath, validator
from typing import Union, Optional
from enum import Enum

from .tasks import Task, TaskStatus, TaskPriority, Indicator
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
    def manual_questions_answered(cls, subject_type: str, values: dict):
        if subject_type is SubjectType.manual:
            if (
                values.get("has_archive") is None
                or values.get("has_archive") is None
                or values.get("has_archive") is None
                or values.get("has_archive") is None
                or values.get("has_archive") is None
                or values.get("has_archive") is None
                or values.get("has_archive") is None
                or values.get("has_archive") is None
                or values.get("has_archive") is None
            ):
                raise ValueError("Self-assessments needs the form filled")
        return subject_type


class Session(BaseModel):
    id: str
    subject: Union[HttpUrl, FileUrl, FilePath, None]
    tasks: dict[str, Task] = {}
    status: SessionStatus = SessionStatus.queued
    score_all_essential: Optional[float]
    score_all_nonessential: Optional[float]
    score_all: Optional[float]
    score_applicable_essential: Optional[float]
    score_applicable_nonessential: Optional[float]
    score_applicable_all: Optional[float]


class SessionHandler:
    def __init__(self, session_data: SessionSubjectIn) -> None:
        self.id = str(uuid4())

        self.user_input = session_data
        self.session_model = Session(id=self.id, subject=session_data.path)
        self.create_tasks()

        self.metadata = {}
        self.retrieve_metadata(self.session_model.subject)

    def retrieve_metadata(self, url: str) -> None:
        # See what is possible here
        pass

    def is_running(self):
        return any([task.status is TaskStatus.queued or task.status is TaskStatus.started for task in self.session_model.tasks.values()])

    def run_statistics(self):
        if self.is_running():
            return
        else:
            self._calculate_score_essential()
            self._calculate_score_all()
            self._calculate_na_ratio()

    def _count_essential(self):
        return sum([t.priority is TaskPriority.essential and t.status is not TaskStatus.not_applicable for t in self.session_model.tasks.values()])

    def _count_applicable(self):
        return sum([t.status is not TaskStatus.not_applicable for t in self.session_model.tasks.values()])

    def _calculate_na_ratio(self):
        self.session_model.ratio_not_applicable = sum([t.status is TaskStatus.not_applicable for t in self.session_model.tasks.values()]) / len(self.session_model.tasks)

    def _calculate_score_essential(self):
        self.session_model.score_essential = sum([
            t.score for t in self.session_model.tasks.values() if t.priority is TaskPriority.essential and t.status is not TaskStatus.not_applicable
        ]) / self._count_essential()

    def _calculate_score_all(self):
        self.session_model.score_all = sum([t.score for t in self.session_model.tasks.values() if t.status is not TaskStatus.not_applicable]) / self._count_applicable()

    def create_tasks(self):
        for indicator in fair_indicators.values():
            key, task = self._create_task(indicator)
            self.session_model.tasks[key] = task

    def _create_task(self, indicator: Indicator):
        task_id = str(uuid4())
        task_status = TaskStatus.queued
        disabled = False

        if self.should_disable_task(indicator):
            task_status = TaskStatus.failed
            disabled = True

        return task_id, Task(id=task_id, name=indicator.name, priority=TaskPriority(indicator.priority), status=task_status, session_id=self.id, disabled=disabled)

    def should_disable_task(self, indicator: Indicator):
        config = get_settings()

        return (
            self.user_input.subject_type is SubjectType.manual
        ) and (
            (
                not self.user_input.has_archive
                and indicator.name in config.archive_indicators
            ) or (
                not self.user_input.has_archive_metadata
                and indicator.name in config.archive_metadata_indicators
            )
        )

    def json(self):
        return self.session_model.json()
