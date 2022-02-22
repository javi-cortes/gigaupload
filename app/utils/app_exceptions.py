from fastapi import Request
from starlette.responses import JSONResponse


class AppExceptionCase(Exception):
    def __init__(self, status_code: int, context: dict):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            + f"status_code={self.status_code} - context={self.context}>"
        )


async def app_exception_handler(request: Request, exc: AppExceptionCase):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "app_exception": exc.exception_case,
            "context": exc.context,
        },
    )


class AppException(object):
    class FileUploaded(AppExceptionCase):
        def __init__(self, more_context: str = None):
            """
            File creation failed
            """
            status_code = 400
            context = {"error": f"Error uploading the file. {more_context}"}
            AppExceptionCase.__init__(self, status_code, context)

    class FileTooLarge(AppExceptionCase):
        def __init__(self, max_size: int):
            """
            File uploaded too large
            """
            status_code = 413
            context = {"error": f"File too large, cannot exceed {max_size} bytes"}
            AppExceptionCase.__init__(self, status_code, context)

    class TooManyFilesPerUser(AppExceptionCase):
        def __init__(self, max_files: int):
            """
            File uploaded too large
            """
            status_code = 400
            context = {"error": f"File rejected, too many files already ({max_files})"}
            AppExceptionCase.__init__(self, status_code, context)

    class DownloadBytesRateLimit(AppExceptionCase):
        def __init__(self):
            """
            Bytes rate limit per minute
            """
            status_code = 429
            context = {
                "error": f"Byte rate exceeded, wait for the next minute to download"
            }
            AppExceptionCase.__init__(self, status_code, context)

    class FileNotFound(AppExceptionCase):
        def __init__(self):
            """
            File not found
            """
            status_code = 404
            context = {"error": f"File not found"}
            AppExceptionCase.__init__(self, status_code, context)

    class UserCreate(AppExceptionCase):
        def __init__(self, context: dict = None):
            """
            Sub creation failed
            """
            status_code = 400
            AppExceptionCase.__init__(self, status_code, context)

    class ReachedMaxFilesPerUser(AppExceptionCase):
        def __init__(self, max_files: int = 99):
            """
            User can't have more than XX files
            """
            context = {"error": f"Reached maximum files per user: {max_files}"}
            status_code = 400
            AppExceptionCase.__init__(self, status_code, context)
