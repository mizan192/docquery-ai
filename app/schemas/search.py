from pydantic import BaseModel


class SearchRequest(BaseModel):
    # what user sends to API
    question: str        # user question
    top_k: int = 3       # how many similar chunks to find (default 3)


class SearchResponse(BaseModel):
    # what API returns to user
    question: str              # original question
    answer: str                # LLM generated answer
    relevant_chunks: list[str] # chunks used to generate answer
