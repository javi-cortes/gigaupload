from fastapi import APIRouter, Depends

from app import schemas
from app.api.deps import get_db
from app.schemas.user import UserCreate
from app.services.user import UserService
from app.utils.service_result import handle_result

router = APIRouter()


@router.post("", response_model=schemas.User)
async def create_user(user: UserCreate, db: get_db = Depends()):
    result = UserService(db).create_user(user)
    return handle_result(result)
