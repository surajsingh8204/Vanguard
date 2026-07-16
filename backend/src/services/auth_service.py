from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from backend.src.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.src.repositories.user_repository import UserRepository
from backend.src.schemas.user import (
    UserCreate,
    UserLogin,
)


class AuthService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register(
        self,
        user_data: UserCreate,
    ):

        if self.repo.get_by_email(user_data.email):
            raise ValueError("Email already registered.")

        if self.repo.get_by_username(user_data.username):
            raise ValueError("Username already exists.")


        password_hash = hash_password(user_data.password)

        return self.repo.create(
            user_data,
            password_hash,
        )

    def login(
        self,
        credentials: OAuth2PasswordRequestForm,
    ):

        user = self.repo.get_by_email(
            credentials.username
        )

        if not user:
            raise ValueError("Invalid credentials.")

        if not verify_password(
            credentials.password,
            user.password_hash,
        ):
            raise ValueError("Invalid credentials.")

        token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
            },
            timedelta(minutes=60),
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }
