from unittest.mock import patch, AsyncMock, Mock

import pytest
from fastapi import UploadFile, Depends

from app.api.deps import get_db
from app.models import File
from app.schemas import FileQuery
from app.services.file import FileService
from app.utils.app_exceptions import AppException
from app.utils.service_result import ServiceResult


@pytest.mark.asyncio
async def test_upload_file_return_service_result(
    file_service: FileService, file: UploadFile, db: get_db = Depends()
):
    service_result = await file_service.upload_file(file)
    assert isinstance(service_result, ServiceResult)


@pytest.mark.asyncio
@patch(
    "app.services.file.UserService.can_upload_files",
    return_value=False,
)
async def test_user_cant_upload_file_returns_proper_exception(
    can_upload_files: AsyncMock,
    file_service: FileService,
    file: UploadFile,
    db: get_db = Depends(),
):
    service_result = await file_service.upload_file(file)

    assert isinstance(service_result.value, AppException.TooManyFilesPerUser)


@pytest.mark.asyncio
@patch(
    "app.services.file.FileCRUD.store_file",
    return_value=(File(), False),
)
async def test_upload_file_returns_file_model(
    store_file_mock: AsyncMock,
    file_service: FileService,
    file: UploadFile,
    db: get_db = Depends(),
):
    service_result = await file_service.upload_file(file)

    assert isinstance(service_result.value, File)


@pytest.mark.asyncio
@patch(
    "app.services.file.FileCRUD.store_file",
    return_value=(File(), True),
)
@patch(
    "app.services.file.UserService.increase_file_count",
)
async def test_if_is_new_file_user_file_counter_gets_incremented(
    increase_file_count: Mock,
    store_file: AsyncMock,
    file_service: FileService,
    file: UploadFile,
    db: get_db = Depends(),
):
    await file_service.upload_file(file)

    increase_file_count.assert_called()


@pytest.mark.asyncio
@patch(
    "app.services.file.FileCRUD.store_file",
    return_value=(File(), False),
)
@patch(
    "app.services.file.UserService.increase_file_count",
)
async def test_if_its_not_a_new_file_user_file_counter_doesnt_get_incremented(
    increase_file_count: Mock,
    store_file: AsyncMock,
    file_service: FileService,
    file: UploadFile,
    db: get_db = Depends(),
):
    await file_service.upload_file(file)

    increase_file_count.assert_not_called()


@pytest.mark.asyncio
@patch("app.services.file.UserService.can_download_files", return_value=False)
async def test_get_file_uri_returns_exception_when_reached_rate_limit(
    can_download_files: Mock,
    file_service: FileService,
    file_query: FileQuery,
    db: get_db = Depends(),
):
    service_result = await file_service.get_file_uri(file_query)

    can_download_files.assert_called()
    assert isinstance(service_result.value, AppException.DownloadBytesRateLimit)


@pytest.mark.asyncio
@patch(
    "app.services.file.FileCRUD.get_files",
    return_value=[],
)
@patch("app.services.file.UserService.can_download_files", return_value=True)
async def test_get_file_uri_returns_404_when_no_files_found(
    can_download_files: Mock,
    get_files: Mock,
    file_service: FileService,
    file_query: FileQuery,
    db: get_db = Depends(),
):
    service_result = await file_service.get_file_uri(file_query)

    assert isinstance(service_result.value, AppException.FileNotFound)


@pytest.mark.asyncio
@patch(
    "app.services.file.FileCRUD.get_files",
    return_value=[Mock(uri="fakeuri", size=0)],
)
@patch("app.services.file.UserService.can_download_files", return_value=True)
@patch("app.services.file.UserService.update_download_stats", return_value=True)
async def test_get_file_uri_update_download_stats(
    update_download_stats: Mock,
    can_download_files: Mock,
    get_files: Mock,
    file_service: FileService,
    file_query: FileQuery,
    db: get_db = Depends(),
):
    await file_service.get_file_uri(file_query)

    update_download_stats.assert_called()
