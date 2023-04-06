from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional, Dict

class TaskStatus(str, Enum):
    queued = "queued"
    started = "started"
    success = "success"
    failed = "failed"
    warnings = "warnings"
    error = "error"
    not_applicable = "not_applicable"


class TaskPriority(str, Enum):
    essential = "essential"
    important = "important"
    useful = "useful"


class TaskStatusIn(BaseModel):
    status: TaskStatus


class Task(BaseModel):
    id: str
    name: str  # Is it necessary?
    session_id: str  # Needs a validator (https://docs.pydantic.dev/usage/validators/)? This must be a valid id
    children: Dict[str, "Task"] = {}
    priority: TaskPriority = TaskPriority.essential
    status: TaskStatus = TaskStatus.queued
    comment: str = ""
    disabled: bool = False

    score: Optional[float]

    @validator("score", pre=True, always=True)
    def make_score(cls, _, values: dict) -> float:
        # Necessary to check for status as fields failing validation are not included in values
        if "status" in values:
            return {TaskStatus.success.value: 1, TaskStatus.failed.value: 0, TaskStatus.warnings.value: 0.5}.get(values['status'])


class TaskDescription(BaseModel):
    name: str
    group: str
    sub_group: str
    priority: str
    question: str
    short: str
    description: str


