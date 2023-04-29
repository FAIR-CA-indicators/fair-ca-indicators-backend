import tempfile
import pytest

from tests.factories import (
    FileSessionSubjectFactory,
    UrlSessionSubjectFactory,
    ManualSessionSubjectFactory,
)


@pytest.fixture
def file_session_input():
    with tempfile.NamedTemporaryFile(mode="r") as tmp:
        yield FileSessionSubjectFactory(path=tmp.name)


@pytest.fixture
def url_session_input():
    return UrlSessionSubjectFactory()


@pytest.fixture
def manual_session_input():
    return ManualSessionSubjectFactory()
