import pytest

from pydantic import ValidationError

from app.models import TaskStatus, IndicatorDependency
from tests.factories import TaskFactory


# FIXME: Will change if we make score dependent on TaskPriority
@pytest.mark.parametrize(
    "status",
    [
        TaskStatus.queued,
        TaskStatus.started,
        TaskStatus.not_answered,
        TaskStatus.not_applicable,
        TaskStatus.failed,
        TaskStatus.success,
        TaskStatus.warnings,
    ],
)
def test_task_validation_make_score(status):
    expected_score = {TaskStatus.success: 1, TaskStatus.warnings: 0.5}.get(status, 0)

    task = TaskFactory()
    assert task.score == 0

    task.status = status
    assert task.score == expected_score


# Needs to be async to access fair_indicators global object
def test_task_validation_valid_name():
    with open("app/metrics/metrics.csv", "r") as metrics_file:
        indicators = [
            line.split(",")[0].strip('"') for line in metrics_file.readlines()
        ]

    indicators = indicators[1:]  # Dropping column name

    for indicator in indicators:
        TaskFactory(name=indicator)

    with pytest.raises(ValidationError):
        TaskFactory(name="Test task")


def test_task_get_task_child():
    task1 = TaskFactory()
    task2 = TaskFactory(session_id=task1.session_id)
    task3 = TaskFactory(session_id=task1.session_id)

    task2.add_task(task3)
    task1.add_task(task2)

    task4 = TaskFactory()

    assert task1.get_task_child(task2.id) is task2
    assert task1.get_task_child(task3.id) is task3
    assert task1.get_task_child(task4.id) is None


def test_indicator_dependency_check_task_dependencies():
    expected_name = "CA-RDA-F1-01Model"
    wrong_name = "CA-RDA-F1-01Archive"

    dependency = IndicatorDependency([expected_name])
    with pytest.raises(ValueError):
        dependency._check_task_dependencies([])

    correct_task = TaskFactory(name=expected_name)
    wrong_task = TaskFactory(name=wrong_name)

    with pytest.raises(ValueError):
        dependency._check_task_dependencies([wrong_task])

    dependency._check_task_dependencies([correct_task])


@pytest.mark.parametrize(
    "parent_status,should_fail",
    [
        (TaskStatus.queued, False),
        (TaskStatus.started, False),
        (TaskStatus.success, False),
        (TaskStatus.failed, True),
        (TaskStatus.warnings, False),
        (TaskStatus.not_applicable, False),
        (TaskStatus.not_answered, False),
        (TaskStatus.error, False),
    ],
)
def test_indicator_dependency_automatic_fail(parent_status, should_fail):
    task_name = "CA-RDA-F1-01Model"
    dependency = IndicatorDependency([task_name])
    task = TaskFactory(name=task_name, status=parent_status)

    assert dependency.is_automatically_failed([task]) == should_fail


@pytest.mark.parametrize(
    "parent_status,should_disable",
    [
        (TaskStatus.queued, True),
        (TaskStatus.started, True),
        (TaskStatus.success, False),
        (TaskStatus.failed, True),
        (TaskStatus.warnings, False),
        (TaskStatus.not_applicable, False),
        (TaskStatus.not_answered, False),
        (TaskStatus.error, False),  # Should it be disabled?
    ],
)
def test_indicator_dependency_automatic_disable(parent_status, should_disable):
    task_name = "CA-RDA-F1-01Model"
    dependency = IndicatorDependency([task_name])
    task = TaskFactory(name=task_name, status=parent_status)

    assert dependency.is_automatically_disabled([task]) == should_disable
