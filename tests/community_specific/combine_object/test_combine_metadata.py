import pytest

from app.models import CombineArchive, CombineArchiveException


def compare_metadata(expected, found):
    assert len(found) == len(expected), "All entries in metadata should be tested"
    for key, expected_value in expected.items():
        found_value = found[key]
        if isinstance(found_value, list):
            assert len(found_value) == len(
                expected_value
            ), f"Found {key} should have {len(expected_value)} entries"
            assert sorted(found_value) == sorted(
                expected_value
            ), f"{key} should contain the same values"
        else:
            assert found[key] == expected_value, f"{key} should contain the same values"


# TODO: Test the following files
#   - Ai2021PhysiomeS000013.omex
#   - case_01.omex
#   - Elowitz_Leibler_2000.omex
#   - SMC_excitation_contraction.omex


@pytest.mark.parametrize(
    "filename, is_archive",
    [
        ("tests/data/omex/CombineArchiveShowCase.omex", True),
        ("tests/data/sbml/BIOMD0000000144.xml", False),
        ("tests/data/sbml/BIOMD0000000640_url.xml", False),
        ("tests/data/sbml/Human-GEM.xml", False),
        ("tests/data/sbml/model.xml", False),
        ("tests/data/cellml/elowitz_leibler_2000.cellml", False),
    ],
)
def test_model_metadata_from_omex(filename, is_archive):
    ca = CombineArchive(filename, file_is_archive=is_archive)

    metadata = ca.main_model_metadata
    found_data = metadata.dict()
    expected_data = {
        "tests/data/omex/CombineArchiveShowCase.omex": {
            "taxa": [],
            "properties": [],
            "alt_ids": [
                "http://identifiers.org/biomodels.db/BIOMD0000000144",
                "http://identifiers.org/biomodels.db/MODEL1509031628",
            ],
            "versions": [
                "http://identifiers.org/obo.go/GO:0000278",
                "http://identifiers.org/obo.go/GO:0051783",
            ],
            "creators": ["Nicolas Le Novère", "Enuo He", "Laurence Calzone"],
            "creation_date": "2007-06-08T08:29:58Z",
            "modification_dates": [
                "2008-03-28T00:00:00Z",
                "2008-08-21T00:00:00Z",
                "2008-12-03T00:00:00Z",
                "2009-03-25T00:00:00Z",
                "2009-09-02T00:00:00Z",
                "2010-01-26T00:00:00Z",
                "2010-09-30T00:00:00Z",
                "2011-04-15T00:00:00Z",
                "2012-02-08T00:00:00Z",
                "2012-05-20T00:00:00Z",
                "2012-07-05T16:48:32Z",
                "2012-08-11T00:00:00Z",
                "2012-12-12T00:00:00Z",
            ],
            "cell_locations": ["http://identifiers.org/taxonomy/7215"],
            "citations": ["http://identifiers.org/pubmed/17667953"],
        },
        "tests/data/omex/Roda2020.omex": {
            "taxa": [
                "urn:miriam:taxonomy:2697049",
                "urn:miriam:taxonomy:9606",
                "http://identifiers.org/taxonomy/2697049",
                "http://identifiers.org/taxonomy/9606",
            ],
            "properties": [
                "urn:miriam:mamo:MAMO_0000028",
                "urn:miriam:mamo:MAMO_0000046",
                "http://identifiers.org/mamo/MAMO_0000028",
                "http://identifiers.org/mamo/MAMO_0000046",
            ],
            "alt_ids": [],
            "versions": [
                "urn:miriam:doid:DOID:0080600",
                "http://identifiers.org/doid/DOID:0080600",
            ],
            "creators": ["Kausthubh Ramachandran"],
            "creation_date": "2020-07-13T17:19:55Z",
            "modification_dates": ["2020-07-13T17:19:55Z"],
            "cell_locations": [],
            "citations": [
                "http://identifiers.org/pubmed/32289100",
                "urn:miriam:pubmed:32289100",
            ],
        },
        "tests/data/sbml/BIOMD0000000144.xml": {
            "taxa": [],
            "properties": [],
            "alt_ids": [
                "http://identifiers.org/biomodels.db/MODEL1509031628",
                "http://identifiers.org/biomodels.db/BIOMD0000000144",
            ],
            "versions": [
                "http://identifiers.org/obo.go/GO:0000278",
                "http://identifiers.org/obo.go/GO:0051783",
            ],
            "creators": ["Nicolas Le Novère", "Enuo He", "Laurence Calzone"],
            "creation_date": "2007-06-08T08:29:58Z",
            "modification_dates": [
                "2012-07-05T16:48:32Z",
            ],
            "cell_locations": ["http://identifiers.org/taxonomy/7215"],
            "citations": ["http://identifiers.org/pubmed/17667953"],
        },
        "tests/data/sbml/BIOMD0000000640_url.xml": {
            "taxa": ["http://identifiers.org/taxonomy/40674"],
            "properties": [
                "http://identifiers.org/go/GO:0010506",
                "http://identifiers.org/mamo/MAMO_0000046",
            ],
            "alt_ids": [
                "http://identifiers.org/biomodels.db/MODEL1702270000",
                "http://identifiers.org/biomodels.db/BIOMD0000000640",
            ],
            "versions": [],
            "creators": ["Piero Dalle Pezze", "Varun Kothamachu"],
            "creation_date": "2015-05-07T15:00:48Z",
            "modification_dates": ["2017-05-22T07:24:09Z"],
            "cell_locations": [],
            "citations": [
                "http://identifiers.org/pubmed/27869123",
            ],
        },
        "tests/data/sbml/model.xml": {
            "taxa": [
                "urn:miriam:taxonomy:2697049",
                "urn:miriam:taxonomy:9606",
                "http://identifiers.org/taxonomy/2697049",
                "http://identifiers.org/taxonomy/9606",
            ],
            "properties": [
                "urn:miriam:mamo:MAMO_0000028",
                "urn:miriam:mamo:MAMO_0000046",
                "http://identifiers.org/mamo/MAMO_0000028",
                "http://identifiers.org/mamo/MAMO_0000046",
            ],
            "alt_ids": [],
            "versions": [
                "urn:miriam:doid:DOID:0080600",
                "http://identifiers.org/doid/DOID:0080600",
            ],
            "creators": ["Kausthubh Ramachandran"],
            "creation_date": "2020-07-13T17:19:55Z",
            "modification_dates": ["2020-07-13T17:19:55Z"],
            "cell_locations": [],
            "citations": [
                "http://identifiers.org/pubmed/32289100",
                "urn:miriam:pubmed:32289100",
            ],
        },
        "tests/data/sbml/Human-GEM.xml": {
            "taxa": [],
            "properties": [
                "http://identifiers.org/mamo/MAMO_0000009",
            ],
            "alt_ids": [
                "https://identifiers.org/taxonomy/9606",
            ],
            "versions": [],
            "creators": [],
            "creation_date": "2022-02-06T21:11:50Z",
            "modification_dates": ["2022-02-06T21:11:50Z"],
            "cell_locations": [],
            "citations": [],
        },
        "tests/data/cellml/elowitz_leibler_2000.cellml": {
            "alt_ids": [],
            "versions": [],
            "properties": [],
            "taxa": [],
            "creators": ["Jeelean Lim"],
            "creation_date": "2009-04-02T00:00:00+00:00",
            "modification_dates": [
                "2009-04-30T12:38:21+12:00",
                "2009-04-28T11:49:59+12:00",
            ],
            "cell_locations": [],
            "citations": [],
        },
    }
    compare_metadata(expected_data[filename], found_data)


def test_copasi_metadata():
    with pytest.raises(CombineArchiveException) as exc:
        CombineArchive("tests/data/omex/Roda2020.omex")
    assert "COPASI files are not yet handled by the FairCombine assessment tool" in str(
        exc.value
    )
