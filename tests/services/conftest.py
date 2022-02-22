import pathlib
import uuid

import pytest

from app.schemas import FileQuery
from app.services.file import FileService


@pytest.fixture()
def file_service(db):
    return FileService(db)


@pytest.fixture(scope="session")
def file():
    return open("tests/files_stub/test_file", "wb")


@pytest.fixture(scope="session", autouse=True)
def cleanup(file):
    """Cleanup a testing file once we are finished."""
    file.close()
    file_to_rem = pathlib.Path("tests/files_stub/test_file")
    file_to_rem.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def file_query():
    return FileQuery(uri=uuid.uuid4())
