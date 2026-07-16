from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from backend.src.schemas.message import MessageResponse

class ConversationCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )
class ConversationUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )
class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    messages: list[MessageResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )