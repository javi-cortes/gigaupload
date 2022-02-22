from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.request_exceptions import (
    http_exception_handler,
    request_validation_exception_handler,
)

from app.api.v1.api import api_router, tags_metadata
from app.core.config import settings
from app.utils.app_exceptions import AppExceptionCase
from app.utils.app_exceptions import app_exception_handler


def get_application():
    description = """
    Onna home test 🚀
    
    ## Files
    
    You can **upload files**.
    You can **list files**.
    You can **download files**.
    
    ## Users
    
    You will be able to:
    
    * **Create users**.
    """
    _app = FastAPI(
        title=settings.PROJECT_NAME,
        contact={
            "name": "Javier Cortés Ortega",
            "url": "https://github.com/javi-cortes",
            "email": "javier.cortes.ortega@gmail.com",
        },
        description=description,
        openapi_tags=tags_metadata,
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, e):
    return await http_exception_handler(request, e)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request, e):
    return await request_validation_exception_handler(request, e)


@app.exception_handler(AppExceptionCase)
async def custom_app_exception_handler(request, e):
    return await app_exception_handler(request, e)


app.include_router(api_router, prefix=settings.API_V1_STR)
