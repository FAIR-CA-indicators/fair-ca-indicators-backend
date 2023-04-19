from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional, Dict

from app.metrics.assessments_lifespan import fair_indicators


class TaskStatus(str, Enum):
    """
    Possible status for an assessment task:

    - *queued*: Task was created but has not started yet
    - *started*: Task is currently running
    - *success*: Task passed the FAIR assessment
    - *failed*: Tasks did not pass the FAIR assessment
    - *warnings*: Tasks partially passed the FAIR assessment
    - *error*: An error occurred while the Task was running
    - *not_applicable*: The assessment is not applicable to the model/archive
    - *not_answered*: In self-assessments, the user refused to answer the question
    """
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
    """
    Pydantic model for user to submit a status when editing a Task (see route
    `update_task`)
    """
    status: TaskStatus


class Task(BaseModel):
    """
    The running of a FAIR assessment in one particular Session object

    - *id*: A Task identifier
    - *name*: Name of the indicator assessed by a Task
    - *session_id*: The Session identifier a Task belongs to
    - *children*: Mapping of task identifiers that depends on this Task status to the corresponding
        Task objects
    - *priority*: Describes how important a task is.
    - *status*: The task current status (see TaskStatus model)
    - *comment*: Additional comment for a task
    - *disabled*: True if the Task status cannot be edited by user. False otherwise
    - *score*: 1 if Task status is **success**, 0 if **failed**, 0.5 if **warnings**, null otherwise.
    """
    id: str
    name: str
    session_id: str  # Needs a validator (https://docs.pydantic.dev/usage/validators/)? This must be a valid id
    children: Dict[str, "Task"] = {}
    priority: TaskPriority = TaskPriority.essential
    status: TaskStatus = TaskStatus.queued
    comment: str = ""
    disabled: bool = False

    score: float = 0

    @validator("score", pre=True, always=True)
    def make_score(cls, _, values: dict) -> float:
        """
        Calculate the score based on the Task status. This erases possible user
        input in case someone would cheat.

        :param _: The score inputted by user. Not used, but needs to be set
        :param values: The list of values in the Pydantic object
        :return: Score value calculated based on Task status
        """
        # Necessary to check for status as fields failing validation are not included in values
        if "status" in values:
            return {
                TaskStatus.success.value: 1,
                TaskStatus.failed.value: 0,
                TaskStatus.warnings.value: 0.5,
            }.get(values['status'], 0)
        else:
            raise ValueError("Task status is required to calculate a score")

    @validator("name")
    def has_valid_name(cls, name: str) -> str:
        """
        Asserts that the assessment name given for the task exists in the FAIR indicators
        (see `app/metrics/metrics.csv`)
        :param name: The name given by the user
        :return: The valid assessment name
        """
        if name not in fair_indicators:
            raise ValueError("Given assessment name is not a known indicator")
        return name

    def get_task_child(self, child_id: str) -> Optional["Task"]:
        """
        Returns the Task associated with `child_id` if is part of the children
        of this task

        :param child_id: The child Task identifier
        :return: The child Task or None if the Task object was not found in children
        """
        if self.children and child_id in self.children:
            return self.children[child_id]
        else:
            for child in self.children.values():
                task = child.get_task_child(child_id)
                if task is not None:
                    return task

    def is_running_or_failed(self):
        """
        Checks whether the tasks is still running or if it has failed

        :return: False if the task is either passed (with or without warnings),
        not applicable, or not answered. True otherwise
        """
        return (
            self.status != "success"
            and self.status != "warning"
            and self.status != "not_applicable"
            and self.status != "not_answered"
        )


class Indicator(BaseModel):
    """
    Pydantic model for a FAIR assessment

    - *name*: The name of the assessment
    - *group*: The FAIR group an assessment belongs to (e.g. 'F', or 'A')
    - *sub_group*: The FAIR subgroup an assessment belongs to (e.g. `F1`, or `I3`)
    - *priority*: How important this assessment is
    - *question*: The question asked for this assessment
    - *short*: A short description of the assessment
    - *description*: A in-depth description of the assessment
    """
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
        - if `indicator1` depends on `indicator2`, `indicator1` is disabled and its
            status is automatically set at `failed` if `indicator2` is failed
        - if `indicator1` depends on `indicator2` AND `indicator3`, `indicator1` is
            disabled and its status is automatically set at `failed` if either
            `indicator2` OR `indicator3` is failed (DependencyType.and_)
        - if `indicator1` depends on `indicator2` OR `indicator3`, `indicator1` is
            disabled and its status is automatically set at `failed` if both
            `indicator2` AND `indicator3` are failed (DepedencyType.or_)
    """
    def __init__(self, dependencies: list[str], operation: DependencyType = "or"):
        if len(dependencies) != len(set(dependencies)):
            raise ValueError("List of dependencies contains duplicates")

        self.dependencies = dependencies
        self.operation = DependencyType(operation)

    def _check_task_dependencies(self, dependencies: list["Task"]) -> None:
        """
        Checks whether the Task given to other methods are corresponding to
        the indicators defined at initialization

        :param dependencies: List of Tasks a TaskStatus depends on
        :return: None
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
        Step1: Checks that dependencies contain all correct indicators (no more no less than what it was initialised with)
        Step2: Applies the dependencies combination to determine whether task should be automatically failed
        If dependency is `or`, Task is automatically failed if any dependency is failed.
        If dependency is `and`, Task is automatically failed if all dependencies are failed.

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
        If dependency type is `or`, Task is disabled if any dependency has not passed yet
        If dependency type is `and`, Task is disabled if no dependency has passed

        :param dependencies: The list of tasks `task` depends on. The dependencies must correspond with
            the list of indicators given at this object initialisation.

        :return: True if the given task should be automatically failed
        """
        self._check_task_dependencies(dependencies)
        if self.operation is DependencyType.or_:
            return any([d.is_running_or_failed() for d in dependencies])
        elif self.operation is DependencyType.and_:
            return all([d.is_running_or_failed() for d in dependencies])

