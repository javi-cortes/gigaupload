import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse

from app import schemas
from app.api.deps import get_db
from app.services.file import FileService
from app.utils.service_result import handle_result

router = APIRouter()


@router.post("/", response_model=schemas.FileCreated, status_code=201)
async def upload_file(file: UploadFile = File(...), db: get_db = Depends()):
    """
    Uploads a file to the system.
    """
    result = await FileService(db).upload_file(file)
    return handle_result(result)


@router.get("/", response_model=List[schemas.FileCreated])
async def get_all_files(db: get_db = Depends()):
    """
    Returns all files on the user space
    """
    result = await FileService(db).get_files()
    return handle_result(result)


@router.get("/{file_uuid}", response_class=FileResponse)
async def get_file(file_uuid: uuid.UUID, db: get_db = Depends()):
    """
    Returns file for the given uuid identifier
    """
    result = await FileService(db).get_file_uri(schemas.FileQuery(uri=file_uuid))
    return handle_result(result)
