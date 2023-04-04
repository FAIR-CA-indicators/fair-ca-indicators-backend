from pydantic import BaseModel, HttpUrl, FileUrl, FilePath, Field
from typing import Union, Optional, Dict
from .tasks import Task, TaskStatus, TaskPriority
from enum import Enum


class SessionStatus(str, Enum):
    queued = "queued"
    preprocessing = "preprocessing"
    running = "running"
    postprocessing = "postprocessing"
    finished = "finished"
    error = "error"


class Session(BaseModel):
    id: str
    subject: Union[HttpUrl, FileUrl, FilePath]
    tasks: Dict[str, Task] = {}
    status: SessionStatus = SessionStatus.queued
    score_essential: Optional[float]
    score_all: Optional[float]
    ratio_not_applicable: Optional[float]


class SessionHandler:
    def __init__(self, session: Session) -> None:
        self.id = session.id
        self.session_model = session
        self.metadata = {}
        self.retrieve_metadata(self.session_model.subject)

    def retrieve_metadata(self, url: str) -> None:
        # See what is possible here
        pass

    def is_running(self):
        return any([t.status is TaskStatus.queued or t.status is TaskStatus.started for t in self.session_model.tasks])

    def run_statistics(self):
        if self.is_running():
            return
        else:
            self._calculate_score_essential()
            self._calculate_score_all()
            self._calculate_na_ratio()

    def _count_essential(self):
        return sum([t.priority is TaskPriority.essential and t.status is not TaskStatus.not_applicable for t in self.session_model.tasks])

    def _count_applicable(self):
        return sum([t.status is not TaskStatus.not_applicable for t in self.session_model.tasks])

    def _calculate_na_ratio(self):
        self.session_model.ratio_not_applicable = sum([t.status is TaskStatus.not_applicable for t in self.session_model.tasks]) / len(self.session_model.tasks)

    def _calculate_score_essential(self):
        self.session_model.score_essential = sum([
            t.score for t in self.session_model.tasks if t.priority is TaskPriority.essential and t.status is not TaskStatus.not_applicable
        ]) / self._count_essential()

    def _calculate_score_all(self):
        self.session_model.score_all = sum([t.score for t in self.session_model.tasks if t.status is not TaskStatus.not_applicable]) / self._count_applicable()

    def json(self):
        return self.session_model.json()
