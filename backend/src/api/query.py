from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from backend.src.auth.dependencies import get_current_user
from backend.src.database.session import get_db
from backend.src.models.user import User

from backend.src.schemas.query import QueryRequest
from backend.src.schemas.query import QueryResponse
from backend.src.schemas.conversation import ConversationCreate

from backend.src.repositories.conversation_repository import ConversationRepository
from backend.src.repositories.message_repository import MessageRepository

from backend.src.services.ai_service import ask

router = APIRouter(
    prefix="/query",
    tags=["Intelligence"],
)


@router.post(
    "/",
    response_model=QueryResponse,
)
def query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:

        conversation_repo = ConversationRepository(db)
        message_repo = MessageRepository(db)

        # Create conversation if not provided
        if request.conversation_id is None:

            conversation = conversation_repo.create(
                current_user.id,
                ConversationCreate(
                    title=request.question[:50]
                ),
            )

        else:

            conversation = conversation_repo.get_by_id(
                request.conversation_id
            )

            if conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found",
                )

        # Save user message
        message_repo.create(
            conversation_id=conversation.id,
            role="user",
            content=request.question,
        )

        # Ask AI
        result = ask(request.question)

        if isinstance(result, tuple):
            answer, stats = result
        else:
            answer = result
            stats = {}

        # Save assistant message
        message_repo.create(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
        )

        return QueryResponse(
            answer=answer,
            retrieval_stats=stats,
            conversation_id=conversation.id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )