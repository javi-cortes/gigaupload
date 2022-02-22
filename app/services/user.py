from datetime import datetime

import sqlalchemy
from loguru import logger

from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserIncreaseFileCount,
    UpdateUserDownloadStats,
)
from app.services.main import AppService, AppCRUD
from app.utils.app_exceptions import AppException
from app.utils.service_result import ServiceResult


class UserService(AppService):
    MAX_FILES_PER_USER = 2
    MAX_BYTES_PER_MINUTE = 1024 * 1024  # 1 MB

    def create_user(self, user: UserCreate) -> ServiceResult:
        new_user = UserCRUD(self.db).create_user(user)
        if not new_user:
            return ServiceResult(
                AppException.UserCreate(context={"error": "Error creating user"})
            )
        return ServiceResult(new_user)

    def can_upload_files(self, user: User, lock_user=False):
        """
        Checks if the user is able to upload files.

        Current restriction is 99 files per user

        This method will lock the user on the DB. So should be followed
        by a commit somewhere.
        """
        files_count = UserCRUD(self.db).get_files_count_per_user(user.id)

        if not lock_user:
            self.db.commit()

        return files_count < self.MAX_FILES_PER_USER

    def can_download_files(self, user: User, lock_user=False):
        """
        Checks if the user is able to upload files.

        Current restrictions:
            - 1MB per minute

        This method will lock the user on the DB. So should be followed
        by a commit somewhere.
        """
        user = UserCRUD(self.db).get_user(user.id)

        if not lock_user:
            self.db.commit()

        last_download_on_last_minute = (
            datetime.now() - user.last_download_time
        ).seconds < 60

        if not last_download_on_last_minute:
            UserCRUD(self.db).reset_bytes_counter(user)
            return True

        return user.bytes_read_on_last_minute <= self.MAX_BYTES_PER_MINUTE

    def increase_file_count(
        self, increase_amount: UserIncreaseFileCount
    ) -> ServiceResult:
        """
        Increase the number of files a user has
        There's a limitation of 99 files per user, check this beforehand
        :param increase_amount: UserIncreaseFileCount payload
        """
        # suppose only 1 user on the system, otherwise use some auth
        increase_amount.user_id = 1

        result = UserCRUD(self.db).increase_file_count(increase_amount)

        if not result:
            return ServiceResult(
                AppException.UserCreate(
                    context={"error": "Error increasing file count"}
                )
            )
        return ServiceResult(result)

    def update_download_stats(self, user_payload: UpdateUserDownloadStats):
        UserCRUD(self.db).update_last_download_stats(user_payload)


class UserCRUD(AppCRUD):
    def create_user(self, user_create: UserCreate) -> User:
        user = User(**user_create.dict())
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except sqlalchemy.exc.DatabaseError as error:
            logger.error(f"{error}")
            user = None
        return user

    def get_user(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).with_for_update().first()

    def increase_file_count(self, user_payload: UserIncreaseFileCount) -> User:
        result = (
            self.db.query(User)
            .filter(User.id == user_payload.user_id)
            .update({User.files_uploaded: User.files_uploaded + 1})
        )

        try:
            self.db.commit()
        except sqlalchemy.exc.DatabaseError as error:
            logger.error(f"{error}")
            result = None
        self.db.commit()

        return result

    def get_files_count_per_user(self, user_id: int) -> int:
        """
        Obtain the files uploaded per user.
        NOTE: keep in mind this function locks the user row in particular
        until the transaction ends.

        Without db.commit() somewhere this could lead to a permanent locked row
        on the DB
        """
        try:
            return (
                self.db.query(User.files_uploaded)
                .filter(User.id == user_id)
                .with_for_update()
                .first()[0]
            )
        except TypeError:
            # on error unlock
            self.db.commit()

    def update_last_download_stats(self, user_payload: UpdateUserDownloadStats):
        user = self.get_user(user_id=user_payload.user_id)
        user.bytes_read_on_last_minute += user_payload.bytes
        user.last_download_time = datetime.now()

        try:
            self.db.commit()
            self.db.refresh(user)
        except sqlalchemy.exc.DatabaseError as error:
            logger.error(f"{error}")
            return None

        return user

    def reset_bytes_counter(self, user: User):
        user.bytes_read_on_last_minute = 0

        try:
            self.db.commit()
            self.db.refresh(user)
        except sqlalchemy.exc.DatabaseError as error:
            logger.error(f"{error}")
            return None

        return user
