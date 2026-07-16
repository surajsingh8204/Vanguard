from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.auth.dependencies import get_current_user
from backend.src.database.session import get_db
from backend.src.models.user import User
from backend.src.repositories.conversation_repository import ConversationRepository
from backend.src.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
)
from backend.src.services.conversation_service import ConversationService
from backend.src.schemas.conversation import ConversationUpdate


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "/",
    response_model=ConversationResponse,
)
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = ConversationService(
        ConversationRepository(db)
    )

    return service.create(
        current_user,
        data,
    )


@router.get(
    "/",
    response_model=list[ConversationResponse],
)
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = ConversationService(
        ConversationRepository(db)
    )

    return service.list(current_user)

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = ConversationService(
        ConversationRepository(db)
    )

    try:

        return service.get(
            conversation_id,
            current_user,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )



@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = ConversationService(
        ConversationRepository(db)
    )

    try:

        return service.update(
            conversation_id,
            current_user,
            data,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = ConversationService(
        ConversationRepository(db)
    )

    try:
        service.delete(
            conversation_id,
            current_user,
        )

        return {"message": "Conversation deleted."}

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
