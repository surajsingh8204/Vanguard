from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.src.database.session import get_db
from backend.src.repositories.user_repository import UserRepository
from backend.src.schemas.auth import LoginResponse
from backend.src.schemas.user import UserCreate

from backend.src.schemas.user import UserResponse
from backend.src.services.auth_service import AuthService

from backend.src.auth.dependencies import get_current_user
from backend.src.models.user import User

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        service = AuthService(UserRepository(db))
        return service.register(user)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    credentials: OAuth2PasswordRequestForm= Depends(),
    db: Session = Depends(get_db),
):
    try:
        service = AuthService(UserRepository(db))
        return service.login(credentials)

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),

        )
    

@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return current_user
