from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.chunk import Chunk
from app.schemas.search import SearchRequest, SearchResponse
from app.services.embedding import generate_embedding
from app.services.llm import generate_answer


router = APIRouter(prefix="/api/v1", tags=["Search"])


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    # generate embedding for user question
    question_embedding = generate_embedding(request.question)

    # find similar chunks using pgvector cosine distance
    result = await db.execute(
        select(Chunk)
        .order_by(Chunk.embedding.cosine_distance(question_embedding))
        .limit(request.top_k)
    )
    similar_chunks = result.scalars().all()

    # raise error if no chunks found
    if not similar_chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant chunks found"
        )

    # extract chunk texts
    chunk_texts = [chunk.chunk_text for chunk in similar_chunks]

    # generate answer using LLM
    answer = generate_answer(request.question, chunk_texts)

    return SearchResponse(
        question=request.question,
        answer=answer,
        relevant_chunks=chunk_texts
    )
