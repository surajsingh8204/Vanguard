from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.src.auth.dependencies import get_current_user
from backend.src.database.session import get_db

from backend.src.models.user import User
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    total_users = db.query(func.count(User.id)).scalar()

    total_conversations = (
        db.query(func.count(Conversation.id))
        .filter(Conversation.user_id == current_user.id)
        .scalar()
    )

    total_messages = (
        db.query(func.count(Message.id))
        .join(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .scalar()
    )

    return {
        "total_users": total_users,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "pipeline_status": "Ready",
        "vector_db_status": "Ready",
        "documents_indexed": 5864,
    }