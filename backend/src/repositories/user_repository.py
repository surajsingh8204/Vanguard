from typing import Optional

from sqlalchemy.orm import Session

from backend.src.models.user import User
from backend.src.schemas.user import UserCreate


class UserRepository:
    """
    Handles all database operations related to users.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def get_by_username(self, username: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )

    def create(
        self,
        user_data: UserCreate,
        password_hash: str,
    ) -> User:

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def update(self, user: User):

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def delete(self, user: User):

        self.db.delete(user)
        self.db.commit()
