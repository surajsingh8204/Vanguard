from pydantic import BaseModel

from backend.src.schemas.user import UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginResponse(Token):
    user: UserResponse
