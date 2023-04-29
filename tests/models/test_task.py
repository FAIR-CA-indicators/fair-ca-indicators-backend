import pytest

from app.models import Task, TaskStatus, IndicatorDependency


# Will change if we make score dependent on TaskPriority
@pytest.mark.parametrize("status", [
    TaskStatus.queued,
    TaskStatus.started,
    TaskStatus.not_answered,
    TaskStatus.not_applicable,
    TaskStatus.failed,
    TaskStatus.success,
    TaskStatus.warnings,

])
def test_task_validation_make_score(status):
    pass


# Needs to be async to access fair_indicators global object
def test_task_validation_valid_name():
    pass


def test_task_get_task_child():
    pass


def test_indicator_dependency_check_dependencies():
    pass


def test_indicator_dependency_automatic_fail():
    pass


def test_indicator_dependency_automatic_disable():
    pass

