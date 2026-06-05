# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from app.config import settings
from app.schemas.chat import SourceCitation
from typing import List

class SearchRequest(BaseModel):
    # what user sends to API
    question: str        # user question
    top_k: int = settings.DEFAULT_TOP_K       # how many similar chunks to find (default 3)


class SearchResponse(BaseModel):
    # what API returns to user
    question: str              # original question
    answer: str                # LLM generated answer
    relevant_chunks: list[str] # chunks used to generate answer
    sources: List[SourceCitation]  # list of sources used to generate answer
