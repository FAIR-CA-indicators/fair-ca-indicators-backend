import pytest

from app.models import CombineArchive, CombineArchiveException


@pytest.mark.parametrize(
    "filename",
    [
        "tests/data/omex/CombineArchiveShowCase.omex",
        "tests/data/omex/case_01.omex",
        "tests/data/omex/Elowitz_Leibler_2000.omex",
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


def test_copasi_metadata():
    with pytest.raises(CombineArchiveException) as exc:
        CombineArchive("tests/data/omex/Roda2020.omex")
    assert "COPASI files are not yet handled by the FairCombine assessment tool" in str(
        exc.value
    )


@pytest.mark.parametrize(
    "filename",
    [
        "tests/data/omex/Ai2021PhysiomeS000013.omex",
        "tests/data/omex/SMC_excitation_contraction.omex",
    ],
)
def test_no_master_file_in_manifest(filename):
    with pytest.raises(CombineArchiveException) as exc:
        CombineArchive(filename)
    assert "No master file was defined in provided archive manifest" in str(exc.value)
