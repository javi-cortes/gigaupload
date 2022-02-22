from fastapi import APIRouter

from app.api.v1.endpoints import files, user

api_router = APIRouter()
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(user.router, prefix="/users", tags=["users"])


tags_metadata = [
    {
        "name": "files",
        "description": "Upload and list files.",
    },
    {
        "name": "users",
        "description": "Operations with users",
    },
]
