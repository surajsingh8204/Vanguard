from backend.src.models.user import User
from backend.src.repositories.conversation_repository import ConversationRepository
from backend.src.schemas import conversation
from backend.src.schemas.conversation import ConversationCreate
from backend.src.schemas.conversation import ConversationUpdate


class ConversationService:

    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    def create(
        self,
        current_user: User,
        data: ConversationCreate,
    ):
        return self.repo.create(
            current_user.id,
            data,
        )

    def list(
        self,
        current_user: User,
    ):
        return self.repo.get_all(
            current_user.id
        )
    

    def get(
        self,
        conversation_id: int,
        current_user: User,
    ):

        conversation = self.repo.get_by_id(
        conversation_id
    )

        if conversation is None:
            raise ValueError(
                "Conversation not found."
        )

        if conversation.user_id != current_user.id:
            raise ValueError(
                "Access denied."
        )

        return conversation
    def update(
        self,
        conversation_id: int,
        current_user: User,
        data: ConversationUpdate,
    ):

        conversation = self.repo.get_by_id(
            conversation_id
        )

        if conversation is None:
            raise ValueError(
            "Conversation not found."
        )

        if conversation.user_id != current_user.id:
            raise ValueError(
                "Access denied."
        )

        return self.repo.update(
            conversation,
            data,
        )



    def delete(
        self,
        conversation_id: int,
        current_user: User,
    ):

        conversation = self.repo.get_by_id(
            conversation_id
        )

        if conversation is None:
            raise ValueError(
                "Conversation not found."
            )

        if conversation.user_id != current_user.id:
            raise ValueError(
                "Access denied."
            )

        self.repo.delete(conversation)
