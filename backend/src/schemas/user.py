from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


class UserCreate(BaseModel):
    """
    User registration request.
    """

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100,
    )


class UserLogin(BaseModel):
    """
    User login request.
    """

    email: EmailStr

    password: str


class UserResponse(BaseModel):
    """
    User information returned to client.
    """

    id: int

    username: str

    email: EmailStr

    role: str

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
