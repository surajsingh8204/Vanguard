from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    conversation_id: int | None = None


class QueryResponse(BaseModel):
    answer: str
    retrieval_stats: dict
    conversation_id: int