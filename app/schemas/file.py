import uuid
from datetime import datetime

from pydantic import BaseModel, validator

from app.core.config import settings


class File(BaseModel):
    uri: str
    name: str
    uploaded_on: datetime
    user_id: int

    class Config:
        orm_mode = True


class FileCreated(BaseModel):
    name: str
    uri: uuid.UUID

    @validator("uri")
    def add_path_to_uri(cls, value):
        return f"{settings.API_V1_STR}/files/{value}"

    class Config:
        orm_mode = True


class FileQuery(BaseModel):
    uri: uuid.UUID
