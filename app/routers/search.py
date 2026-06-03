from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.chunk import Chunk
from app.schemas.search import SearchRequest, SearchResponse
from app.services.embedding import generate_embedding
from app.services.llm import generate_answer
from app.core.exceptions import NoChunksFound
from app.core.logging import logger
from app.models.document import Document
from app.core.security import get_current_user
from app.models.user import User
from app.services.rag import get_rag_answer


router = APIRouter(prefix="/api/v1", tags=["Search"])


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    logger.info(f"Search by: {current_user.email}")

    # use RAG service - search only in current user documents
    answer, chunk_texts, sources = await get_rag_answer(
        question=request.question, 
        user_id=current_user.id, 
        db=db, 
        top_k=request.top_k
    )

    if not chunk_texts:
        logger.warning("No chunks found for question")
        raise NoChunksFound()
    
    return SearchResponse(
        question=request.question,
        answer=answer,
        relevant_chunks=chunk_texts
    )
