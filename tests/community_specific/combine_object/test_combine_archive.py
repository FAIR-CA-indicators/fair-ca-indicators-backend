import pytest

from app.models import CombineArchive


@pytest.mark.parametrize(
    "filename",
    [
        "tests/data/omex/CombineArchiveShowCase.omex",
        "tests/data/omex/Roda2020.omex",
    ],
)
def test_combine_archive_init_from_archive(filename):
    ca = CombineArchive(filename)
    assert ca is not None
    assert ca.is_from_archive
    assert ca.locations != []
    assert ca.main_model_object is not None
    assert ca.main_model_location is not None
    assert ca.main_model_metadata is not None


@pytest.mark.parametrize(
    "filename",
    [
        "tests/data/sbml/model.xml",
        "tests/data/sbml/BIOMD0000000144.xml",
    ],
)
def test_combine_archive_init_from_sbml(filename):
    ca = CombineArchive(filename, file_is_archive=False)

    assert ca is not None
    assert not ca.is_from_archive
    assert ca.locations == []
    assert ca.main_model_object is not None
    assert ca.main_model_location is None
    assert ca.main_model_metadata is not None
