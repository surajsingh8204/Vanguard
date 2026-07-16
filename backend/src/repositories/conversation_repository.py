from typing import List, Optional

from sqlalchemy.orm import Session

from backend.src.models import conversation
from backend.src.models.conversation import Conversation
from backend.src.schemas.conversation import ConversationCreate
from sqlalchemy.orm import joinedload
from backend.src.schemas.conversation import ConversationUpdate


class ConversationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        data: ConversationCreate,
    ) -> Conversation:

        conversation = Conversation(
            user_id=user_id,
            title=data.title,
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_by_id(
        self,
        conversation_id: int,
    ):

        return (
            self.db.query(Conversation)
            .options(
                joinedload(Conversation.messages)
        )
        .filter(
                Conversation.id == conversation_id
        )
        .first()
    )
    def get_all(
        self,
        user_id: int,
    ) -> List[Conversation]:

        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    def delete(
        self,
        conversation: Conversation,
    ):

        self.db.delete(conversation)
        self.db.commit()
    def update(
        self,
        conversation: Conversation,
        data: ConversationUpdate,
    ) -> Conversation:

        conversation.title = data.title

        self.db.commit()
        self.db.refresh(conversation)

        return conversation