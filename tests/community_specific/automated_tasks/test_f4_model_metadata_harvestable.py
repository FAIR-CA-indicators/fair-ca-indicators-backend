import pytest

from app.celery.automated_tasks import f4_model_metadata_harvestable
from app.models import SessionHandler, TaskStatus
from tests.factories import FileSessionSubjectFactory


@pytest.mark.parametrize(
    "filename, expected_status",
    [
        ("tests/data/omex/CombineArchiveShowCase.omex", TaskStatus.success),
        ("tests/data/omex/case_01.omex", TaskStatus.failed),
        ("tests/data/omex/Elowitz_Leibler_2000.omex", TaskStatus.success),
        ("tests/data/sed-ml/zhao2013_fig3a-user.sedx", TaskStatus.success),
        ("tests/data/sbml/BIOMD0000000144.xml", TaskStatus.success),
        ("tests/data/sbml/BIOMD0000000640_url.xml", TaskStatus.success),
        ("tests/data/sbml/Human-GEM.xml", TaskStatus.success),
        ("tests/data/sbml/model.xml", TaskStatus.success),
        ("tests/data/cellml/elowitz_leibler_2000.cellml", TaskStatus.success),
    ],
)
@pytest.mark.anyio
async def test_f4_model_metadata_harvestable_task(
    test_asyncclient, filename, expected_status
):
    # Use a factory to load a combine archive/model to the session
    # Make sure to have both working situations
    # Call the celery task
    session_subject = FileSessionSubjectFactory(path=filename)
    assert session_subject.path == filename
    id = "test_session"
    session_handler = SessionHandler.from_user_input(id, session_subject)

    assessed_task_id = session_handler.get_task_from_indicator("CA-RDA-F4-01MM")
    assessed_task = session_handler.session_model.get_task(assessed_task_id)

    assert session_handler.assessed_data is not None
    assert assessed_task is not None

    status = f4_model_metadata_harvestable(
        assessed_task.dict(), session_handler.assessed_data.dict(), True
    )

    assert status == expected_status
