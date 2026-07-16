from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    confidence: float | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )