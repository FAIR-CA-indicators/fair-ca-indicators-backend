from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional, Dict

from app.metrics.assessments_lifespan import fair_indicators

class TaskStatus(str, Enum):
    queued = "queued"
    started = "started"
    success = "success"  # Children tasks should be answerable
    failed = "failed"
    warnings = "warnings"
    error = "error"  # Children tasks should be answerable
    not_applicable = "not_applicable"
    not_answered = "not_answered"  # Should not be counted at all. But children tasks should be answerable

class TaskPriority(str, Enum):
    essential = "essential"
    important = "important"
    useful = "useful"


class TaskStatusIn(BaseModel):
    status: TaskStatus


class Task(BaseModel):
    id: str
    name: str
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

    @validator("name")
    def has_valid_name(cls, name: str) -> str:
        if name not in fair_indicators:
            raise ValueError("Given assessment name is not a known indicator")
        return name

    def get_task_child(self, child_id: str) -> "Task":
        if self.children and child_id in self.children:
            return self.children[child_id]
        else:
            for child in self.children.values():
                task = child.get_task_child(child_id)
                if task is not None:
                    return task

    def disables_children(self):
        return (
            self.status != "success"
            and self.status != "warning"
            and self.status != "not_applicable"
            and self.status != "not_answered"
        )


class Indicator(BaseModel):
    name: str
    group: str
    sub_group: str
    priority: str
    question: str
    short: str
    description: str

class DependencyType(str, Enum):
    or_ = "or"  # If any dependency is failed, the assessment is failed
    and_ = "and"  # If all dependencies are failed, the assessment is failed


class IndicatorDependency:
    """
    Represents an indicator dependency on any combination of other dependencies
    Examples:
        - if `indicator1` depends on `indicator2`, `indicator1` is disabled and its status is automatically set at `failed`
            if `indicator2` is failed
        - if `indicator1` depends on `indicator2` AND `indicator3`, `indicator1` is disabled and its status is automatically set at `failed`
            if either `indicator2` OR `indicator3` is failed
        - if `indicator1` depends on `indicator2` OR `indicator3`, `indicator1` is disabled and its status is automatically set at `failed`
            if both `indicator2` AND `indicator3` are failed
    """
    def __init__(self, dependencies: list[str], operation: DependencyType = "or"):
        if len(dependencies) != len(set(dependencies)):
            raise ValueError("List of dependencies contains duplicates")

        self.dependencies = dependencies
        self.operation = DependencyType(operation)

    def _check_task_dependencies(self, dependencies: list["Task"]) -> None:
        """
        Checks that Tasks given go other methods are ones corresponding to the initialization indicators
        If not, raises a ValueError
        """
        indicators = [d.name for d in dependencies]
        if len(indicators) != len(set(indicators)):
            raise ValueError("Tasks given in dependencies contains duplicate assessments")

        if len(indicators) != len(self.dependencies):
            raise ValueError(f"Length of dependencies in parameters ({len(indicators)} is different than length of indicators given at initialization ({len(self.dependencies)}")

        indicators = set(indicators)
        if any([d not in indicators for d in self.dependencies]):
            raise ValueError(f"Some dependencies defined at initialisation are missing")

    def is_automatically_failed(self, dependencies: list["Task"]) -> bool:
        """
        Checks if the Task should be automatically failed based on it dependencies
        Step1: Checks that task has the correct indicator
        Step2: Checks that dependencies contain all correct indicators (no more no less than what it was initialised with)
        Step3: Applies the dependencies combination to determine whether task should be automatically failed

        :param task: The task to check. Task name should be the indicator this object was initialised with
        :param dependencies: The list of tasks `task` depends on. The dependencies must correspond with
            the list of indicators given at this object initialisation.

        :return: True if the given task should be automatically failed
        """
        self._check_task_dependencies(dependencies)

        if self.operation is DependencyType.or_:
            return any([d.status == "failed" for d in dependencies])
        if self.operation is DependencyType.and_:
            return all([d.status == "failed" for d in dependencies])

    def is_automatically_disabled(self, dependencies: list["Task"]) -> bool:
        """
        Checks if a Task should be automatically disabled based on it dependencies
        Step1: Checks that dependencies contain all correct indicators (no more no less than what it was initialised with)
        Step2: Applies the dependencies combination to determine whether task should be automatically disabled

        :param dependencies: The list of tasks `task` depends on. The dependencies must correspond with
            the list of indicators given at this object initialisation.

        :return: True if the given task should be automatically failed
        """
        self._check_task_dependencies(dependencies)
        if self.operation is DependencyType.or_:
            return any([d.disables_children() for d in dependencies])
        elif self.operation is DependencyType.and_:
            return all([d.disables_children() for d in dependencies])

