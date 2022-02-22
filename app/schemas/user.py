from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: Optional[int] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    id: Optional[int] = None
    email: EmailStr = None


class UserIncreaseFileCount(BaseModel):
    user_id: int
    amount: int = 1


class UpdateUserDownloadStats(BaseModel):
    user_id: int
    bytes: int
