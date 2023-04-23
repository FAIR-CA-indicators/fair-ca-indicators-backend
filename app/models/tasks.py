from pydantic import BaseModel, validator, root_validator
from enum import Enum
from typing import Optional, Dict, TYPE_CHECKING

from app.metrics.assessments_lifespan import fair_indicators
from app.celery.celery_app import execute_task

if TYPE_CHECKING:
    from .session import SessionSubjectIn

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
    automated: bool = False

    score: float = 0

    class Config:
        validate_assignment = True

    def add_task(self, child: "Task"):
        self.children.update({child.id: child})

    @root_validator
    def make_score(cls, values: dict) -> dict:
        """
        Calculate the score based on the Task status. This erases possible user
        input in case someone would cheat.

        :param _: The score inputted by user. Not used, but needs to be set
        :param values: The list of values in the Pydantic object
        :return: Score value calculated based on Task status
        """
        # Necessary to check for status as fields failing validation are not included in values
        if "status" in values:
            values["score"] = {
                TaskStatus.success.value: 1,
                TaskStatus.failed.value: 0,
                TaskStatus.warnings.value: 0.5,
            }.get(values["status"], 0)
            return values
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
            self.status != TaskStatus.success
            and self.status != TaskStatus.warnings
            and self.status != TaskStatus.not_applicable
            and self.status != TaskStatus.not_answered
            and self.status != TaskStatus.error
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
            raise ValueError(
                "Tasks given in dependencies contains duplicate assessments"
            )

        if len(indicators) != len(self.dependencies):
            raise ValueError(
                f"Length of dependencies in parameters ({len(indicators)} is different than length of indicators given "
                f"at initialization ({len(self.dependencies)}"
            )

        indicators = set(indicators)
        if any([d not in indicators for d in self.dependencies]):
            raise ValueError("Some dependencies defined at initialisation are missing")

    def is_automatically_failed(self, dependencies: list["Task"]) -> bool:
        """
        Checks if the Task should be automatically failed based on it dependencies
        Step1: Checks that dependencies contain all correct indicators (no more no less than what it was initialised
            with)
        Step2: Applies the dependencies combination to determine whether task should be automatically failed
        If dependency is `or`, Task is automatically failed if any dependency is failed.
        If dependency is `and`, Task is automatically failed if all dependencies are failed.

        :param dependencies: The list of tasks `task` depends on. The dependencies must correspond with
            the list of indicators given at this object initialisation.

        :return: True if the given task should be automatically failed
        """
        self._check_task_dependencies(dependencies)

        if self.operation is DependencyType.or_:
            return any([d.status == TaskStatus.failed for d in dependencies])
        if self.operation is DependencyType.and_:
            return all([d.status == TaskStatus.failed for d in dependencies])

    def is_automatically_disabled(self, dependencies: list["Task"]) -> bool:
        """
        Checks if a Task should be automatically disabled based on it dependencies
        Step1: Checks that dependencies contain all correct indicators (no more no less than what it was initialised
            with)
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


class AutomatedTask(Task):
    metric_path = "fair-test-example"
    metric_version = "0.1.0"
    title = "Example of FairTest implementation"
    # description = """This indicator serves no purpose except being used as a template for other FairCombine tests"""
    topics = ["data"]  # Needs to be standardised!
    authors = "author-orcid"
    test_test = {}  # Contains the urls towards records used for testing the metric

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def execute_metric(self, data: dict):
        self.status = TaskStatus.started
        result = execute_task.apply_async(task=self, data=data)
        self.status = result
        return result

    def evaluate(self, data: dict):
        eval.info(
            f"Running FairCombine example. This test will pass",
        )

        # Retrieving subject of the evaluation (a model or an archive)
        # data = eval.retrieve_metadata(eval.subject)

        # Running some kind of tests on the data (does it contain an id, a license, ...)
        # result = self.execute_metric(data)

        return TaskStatus.success

