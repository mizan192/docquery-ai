from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.config import settings


class ChatRequest(BaseModel):
    # user question
    question: str
    # optional - search specific document
    document_id: Optional[int] = None
    # number of similar chunks to find
    top_k: int = settings.DEFAULT_TOP_K


class SourceCitation(BaseModel):
    # source information for each chunk used
    document_filename: str
    chunk_index: int
    chunk_text: str


class ChatResponse(BaseModel):
    id: int
    question: str
    answer: str
    # list of sources used to generate answer
    sources: List[SourceCitation]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    source_documents: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
