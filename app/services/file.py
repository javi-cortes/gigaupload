import uuid
from typing import List, Tuple

import aiofiles
import sqlalchemy
from fastapi import File, UploadFile
from loguru import logger
from sqlalchemy.orm import Session

from app import schemas
from app.models.file import File as FileModel
from app.schemas import UserIncreaseFileCount, User
from app.schemas.user import UpdateUserDownloadStats
from app.services.main import AppService, AppCRUD
from app.services.user import UserService
from app.utils.app_exceptions import AppException, AppExceptionCase
from app.utils.service_result import ServiceResult


class FileService(AppService):
    PATH_TO_FILES = "uploads/"

    def __init__(self, db: Session):
        super().__init__(db)

    async def upload_file(self, file: UploadFile = File(...)) -> ServiceResult:
        if not UserService(self.db).can_upload_files(User(id=1), lock_user=True):
            return ServiceResult(
                AppException.TooManyFilesPerUser(UserService.MAX_FILES_PER_USER)
            )

        try:
            file, is_new_file = await FileCRUD(self.db).store_file(file)
        except AppExceptionCase as app_exception:
            return ServiceResult(app_exception)

        if is_new_file:
            UserService(self.db).increase_file_count(UserIncreaseFileCount(user_id=1))

        return ServiceResult(file)

    async def get_files(self, file_query: schemas.FileQuery = None) -> ServiceResult:
        files = FileCRUD(self.db).get_files(file_query)
        return ServiceResult(files)

    async def get_file_uri(self, file_query: schemas.FileQuery = None) -> ServiceResult:
        # this lock behaviour could be implemented through a context manager
        # to ensure the unlocking! but for the purpose of a home test...
        if not UserService(self.db).can_download_files(User(id=1), lock_user=True):
            return ServiceResult(AppException.DownloadBytesRateLimit())

        files = FileCRUD(self.db).get_files(file_query)
        try:
            file = files[0]
        except IndexError:
            return ServiceResult(AppException.FileNotFound())

        file_uri = self.PATH_TO_FILES + str(file.uri)

        UserService(self.db).update_download_stats(
            UpdateUserDownloadStats(user_id=1, bytes=file.size)
        )
        return ServiceResult(file_uri)


class FileCRUD(AppCRUD):

    MAX_FILE_SIZE = 1024 * 1024 * 30  # 30 MB max file size

    async def store_file(self, file: UploadFile = File(...)) -> Tuple[FileModel, bool]:
        """
        Persist file in the DB from the given FileUploaded schema
        :param file:
        :return: File object and if its created
        """
        file_uuid, file_size = await self._store_file_on_disk(file)
        file_obj = self.get_file_by_name(file.filename)
        if file_obj:
            return file_obj, False

        file_obj = FileModel(
            name=file.filename,
            # suppose only 1 user on the system, otherwise use some auth or
            # session
            user_id=1,
            uri=file_uuid,
            size=file_size,
        )
        try:
            self.db.add(file_obj)
            self.db.commit()
        except sqlalchemy.exc.DatabaseError as error:
            logger.error(f"{error}")
            file_obj = None

        return file_obj, True

    async def _store_file_on_disk(
        self, file: UploadFile = File(...)
    ) -> Tuple[uuid.UUID, int]:

        file_uuid = uuid.uuid4()
        output_file = f"uploads/{file_uuid}"
        real_file_size = 0

        try:
            async with aiofiles.open(f"{output_file}", "wb") as out_file:
                while content := await file.read(1024):  # async read chunk
                    real_file_size += len(content)
                    if real_file_size > self.MAX_FILE_SIZE:
                        raise AppException.FileTooLarge(self.MAX_FILE_SIZE)
                    await out_file.write(content)  # async write chunk
        except IOError:
            raise AppException.FileUploaded()

        return file_uuid, real_file_size

    def get_files(self, file_query: schemas.FileQuery) -> List[FileModel]:
        """
        Search for files filtering by a given file_query
        :param file_query: FileQuery
        :return: List[File]
        """
        uri = file_query and file_query.uri
        return (
            self.db.query(FileModel)
            .filter(
                # suppose only 1 user on the system, otherwise use some auth or
                # session
                FileModel.user_id == 1,
                not uri or FileModel.uri == uri,
            )
            .all()
        )

    def get_file_by_name(self, file_name: str) -> FileModel:
        """
        Search for files filtering by a given file_query
        :param file_name: FileQuery
        :return: List[File]
        """
        return (
            self.db.query(FileModel)
            .filter(
                # suppose only 1 user on the system, otherwise use some auth or
                # session
                FileModel.user_id == 1,
                FileModel.name == file_name,
            )
            .first()
        )
