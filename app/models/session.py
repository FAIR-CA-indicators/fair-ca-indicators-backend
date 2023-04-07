from uuid import uuid4
from pydantic import BaseModel, HttpUrl, FileUrl, FilePath, validator
from typing import Union, Optional
from enum import Enum

from .tasks import Task, TaskStatus, TaskPriority, Indicator
from app.metrics.assessments_lifespan import fair_indicators

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
    is_model_standard: Optional[bool]
    is_archive_standard: Optional[bool]
    is_model_metadata_standard: Optional[bool]
    is_archive_metadata_standard: Optional[bool]
    is_biomodel: Optional[bool]
    is_pmr: Optional[bool]
    assessment_type: SubjectType

    @validator("assessment_type")
    def manual_questions_answered(cls, assessment_type: str, values: dict):
        if assessment_type is SubjectType.manual:
            if (
                "has_archive" not in values
                or "has_model" not in values
                or "is_model_standard" not in values
                or "is_archive_standard" not in values
                or "is_model_metadata_standard" not in values
                or "is_archive_metadata_standard" not in values
                or "is_biomodel" not in values
                or "is_pmr" not in values
            ):
                raise ValueError("Self-assessments needs the form filled")
        return assessment_type


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

        self.session_model = Session(id=self.id, subject=session_data.path)

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
        return task_id, Task(id=task_id, name=indicator.name, priority=TaskPriority(indicator.priority), status=TaskStatus.queued, session_id=self.id)

    def json(self):
        return self.session_model.json()
