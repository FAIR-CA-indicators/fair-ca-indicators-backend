from app.models import (
    Session,
    SessionHandler,
    SessionStatus,
    TaskStatus,
    TaskPriority,
)
from app.dependencies.settings import get_settings

from tests.factories import (
    ManualSessionSubjectFactory,
    TaskFactory,
    SessionFactory,
    IndicatorFactory,
)


def test_session_get_task():
    session = SessionFactory()
    session_id = session.id

    task = TaskFactory(session_id=session_id)
    task_id = task.id

    session.add_task(task)

    assert session.get_task(task_id) is task


def test_session_get_task_child():
    session = SessionFactory()
    session_id = session.id

    task_parent = TaskFactory(session_id=session_id)

    task_child = TaskFactory(session_id=session_id)
    task_child_id = task_child.id
    task_parent.add_task(task_child)

    session.add_task(task_parent)

    assert session.get_task(task_child_id) is task_child


def test_session_get_missing_task():
    session = SessionFactory()

    task_id = "a-random-number"
    assert session.get_task(task_id) is None


def test_session_handler_from_user_input():
    user_input = ManualSessionSubjectFactory()
    id = "test-session"
    sh = SessionHandler.from_user_input(id, user_input)
    assert isinstance(sh, SessionHandler)
    assert isinstance(sh.session_model, Session)
    assert sh.session_model.status == SessionStatus.queued
    assert sh.session_model.tasks is not None and sh.session_model.tasks != {}


# Probably needs to be async
def test_session_handler_from_session():
    session = SessionFactory()
    session_id = session.id

    task = TaskFactory(session_id=session_id)
    task_id = task.id

    session.add_task(task)

    sh = SessionHandler.from_existing_session(session)
    assert sh is not None
    assert isinstance(sh, SessionHandler)
    assert isinstance(sh.session_model, Session)

    assert session.tasks == {task_id: task}


def test_session_handler_build_task_dict():
    session = SessionFactory()
    session_id = session.id

    task1 = TaskFactory(session_id=session_id)
    task1_id = task1.id
    task1_name = task1.name

    task2 = TaskFactory(session_id=session_id)
    task2_id = task2.id
    task2_name = task2.name

    task3 = TaskFactory(session_id=session_id)
    task3_id = task3.id
    task3_name = task3.name

    task2.add_task(task3)

    session.add_task(task1)
    session.add_task(task2)

    sh = SessionHandler.from_existing_session(session)

    assert sh.indicator_tasks == {
        task1_name: task1_id,
        task2_name: task2_id,
        task3_name: task3_id,
    }


def test_session_handler_is_running():
    session = SessionFactory()
    task1 = TaskFactory(session_id=session.id)
    task2 = TaskFactory(session_id=session.id)

    task1.add_task(task2)
    session.add_task(task1)

    sh = SessionHandler.from_existing_session(session)

    assert sh.is_running()
    task1.status = TaskStatus.success
    assert sh.is_running()
    task2.status = TaskStatus.failed
    assert not sh.is_running()


def test_session_handler_update_session_data_essential_task():
    session = SessionFactory()
    task1 = TaskFactory(session_id=session.id)
    task2 = TaskFactory(session_id=session.id)
    task3 = TaskFactory(session_id=session.id)
    task1.add_task(task3)

    session.add_task(task1)
    session.add_task(task2)

    assert session.score_all == 0

    sh = SessionHandler.from_existing_session(session)
    sh.update_session_data()

    assert session.score_all == 0

    task1.status = TaskStatus.success
    sh.update_task_children(task1.id)
    sh.update_session_data()
    assert session.score_all == 1.0 / 3.0
    assert session.score_all_essential == 1.0 / 3.0
    assert session.score_applicable_essential == 1.0 / 3.0
    assert session.score_all_nonessential == 0
    assert session.score_applicable_nonessential == 0
    assert session.ratio_not_applicable == 0

    task3.status = TaskStatus.not_applicable
    sh.update_session_data()
    assert session.score_all == 1.0 / 3.0
    assert session.score_all_essential == 1.0 / 3.0
    assert session.score_applicable_essential == 0.5
    assert session.score_all_nonessential == 0
    assert session.score_applicable_nonessential == 0
    assert session.ratio_not_applicable == 1.0 / 3.0


def test_session_handler_update_session_data_nonessential_task():
    session = SessionFactory()
    task1 = TaskFactory(
        session_id=session.id, priority=TaskPriority.important, name="CA-RDA-F1-01Model"
    )
    task2 = TaskFactory(session_id=session.id, name="CA-RDA-F1-02Model")
    task3 = TaskFactory(session_id=session.id, name="CA-RDA-I1-01Model")
    task1.add_task(task3)

    session.add_task(task1)
    session.add_task(task2)
    assert session.score_all == 0

    sh = SessionHandler.from_existing_session(session)
    sh.update_session_data()

    assert session.score_all == 0

    task1.status = TaskStatus.success
    sh.update_task_children(task1.id)
    sh.update_session_data()
    assert session.score_all == 1.0 / 3.0
    assert session.score_all_essential == 0
    assert session.score_applicable_essential == 0
    assert session.score_all_nonessential == 1
    assert session.score_applicable_nonessential == 1
    assert session.ratio_not_applicable == 0

    task3.status = TaskStatus.not_applicable
    sh.update_session_data()
    assert session.score_all == 1.0 / 3.0
    assert session.score_all_essential == 0
    assert session.score_applicable_essential == 0
    assert session.score_all_nonessential == 1
    assert session.score_applicable_nonessential == 1
    assert session.ratio_not_applicable == 1.0 / 3.0


def test_session_handler_default_task_status():
    # FIXME: This is one dependency only, we should test all of them at some point
    user_input = ManualSessionSubjectFactory(is_biomodel=True)
    session = SessionFactory(session_subject=user_input)
    task_name = "CA-RDA-A1-04Model"

    # Create a initial task to prevent the handler creating tasks
    task = TaskFactory(session_id=session.id)
    session.add_task(task)

    sh = SessionHandler.from_existing_session(session)

    default_status, default_disabled = sh._get_default_task_status(task_name)
    assert default_status == TaskStatus.success
    assert default_disabled
    new_task = sh._create_task(IndicatorFactory(name=task_name))

    assert new_task.status == TaskStatus.success
    assert new_task.disabled


# Definitely needs to be async to access fair_indicators global object
def test_session_handler_create_tasks():
    # Will fail if metrics changes format
    metrics_file = open(get_settings().indicators_path, "r")
    indicators = [line.split(",")[0].strip('"') for line in metrics_file.readlines()]
    metrics_file.close()
    indicators = indicators[1:]  # Dropping column name

    user_input = ManualSessionSubjectFactory()
    id = "test-session"
    sh = SessionHandler.from_user_input(id, user_input)
    assert sh.session_model.tasks != {}

    for indicator in indicators:
        assert indicator in sh.indicator_tasks
        task_key = sh.get_task_from_indicator(indicator)
        assert sh.session_model.get_task(task_key) is not None


def test_session_handler_update_task_children():
    # FIXME: Dependency choice is specific, we should test all of them at some point
    user_input = ManualSessionSubjectFactory(has_archive=True)
    id = "test-session"
    sh = SessionHandler.from_user_input(id, user_input)

    parent_name = "CA-RDA-I3-01Archive"
    parent_id = sh.get_task_from_indicator(parent_name)
    parent_task = sh.session_model.get_task(parent_id)
    assert parent_task.status == TaskStatus.queued

    child_name = "CA-RDA-I3-02Archive"
    child_id = sh.get_task_from_indicator(child_name)
    child_task = sh.session_model.get_task(child_id)
    assert child_task.disabled
    assert child_task.status == TaskStatus.queued

    parent_task.status = TaskStatus.failed
    sh.update_task_children(parent_id)
    assert child_task.disabled
    assert child_task.status == TaskStatus.failed

    parent_task.status = TaskStatus.success
    sh.update_task_children(parent_id)
    assert not child_task.disabled
    assert child_task.status == TaskStatus.queued


# TODO Not implemented yet
def test_session_handler_retrieve_metadata():
    pass
