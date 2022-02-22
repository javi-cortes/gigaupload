from app.api.deps import get_db
from app.schemas import UserCreate
from app.services.user import UserService


def create_dummy_user():
    user_service = UserService(next(get_db()))
    user_service.create_user(UserCreate(id=1, email="test@user.com"))
    

if __name__ == "__main__":
    try:
        create_dummy_user()
    except:
        ...
