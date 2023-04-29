import pytest

from app.models import SessionSubjectIn
from pydantic import ValidationError


def test_session_subject_in_validation_no_subject():
    json_data = {
        "has_archive": False,
        "has_model": False,
        "has_archive_metadata": False,
        "is_model_standard": False,
        "is_archive_standard": False,
        "is_model_metadata_standard": False,
        "is_archive_metadata_standard": False,
        "is_biomodel": False,
        "is_pmr": False,
        "path": "http://test-example.com",
    }

    with pytest.raises(ValidationError):
        SessionSubjectIn(**json_data)


@pytest.mark.parametrize("missing", [
    "has_archive",
    "has_model",
    "has_archive_metadata",
    "is_model_standard",
    "is_archive_standard",
    "is_model_metadata_standard",
    "is_archive_metadata_standard",
    "is_biomodel",
    "is_pmr",
])
def test_session_subject_in_validation_manual(missing):
    json_data = {
        "subject_type": "manual",
        "has_archive": False,
        "has_model": False,
        "has_archive_metadata": False,
        "is_model_standard": False,
        "is_archive_standard": False,
        "is_model_metadata_standard": False,
        "is_archive_metadata_standard": False,
        "is_biomodel": False,
        "is_pmr": False,
    }

    SessionSubjectIn(**json_data)

    json_data.pop(missing)
    with pytest.raises(ValidationError):
        SessionSubjectIn(**json_data)

@pytest.mark.parametrize("subject", ["url", "file"])
def test_session_subject_in_validation_urlfile(subject):
    json_data = {
        "subject_type": subject,
        "path": "http://test-example.com",
    }

    SessionSubjectIn(**json_data)
    json_data.pop("path")

    with pytest.raises(ValidationError):
        SessionSubjectIn(**json_data)