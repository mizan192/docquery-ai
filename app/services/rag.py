# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Tuple
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.chat import SourceCitation
from app.services.embedding import generate_embedding
from app.services.llm import generate_answer
from app.config import settings
from app.core.logging import logger


async def get_rag_answer(
    question: str,
    user_id: int,
    db: AsyncSession,
    top_k: int = settings.DEFAULT_TOP_K,
    document_id: Optional[int] = None
) -> Tuple[str, List[str], List[SourceCitation]]:

    """
    shared RAG logic used by both search and chat routers
    returns answer, chunk_texts, sources
    """

    # generate embedding for question
    question_embedding = generate_embedding(question)

    # build base query 
    query = select(
        Chunk,
        Document,
        Chunk.embedding.cosine_distance(question_embedding).label("distance")
    ).join(Document).where(Document.user_id == user_id)
    
    # filter by document id if provided 
    if document_id:
        query = query.where(Document.id == document_id)

    # find similar chunks using pgvector cosine distance  
    query = query.order_by( 
        Chunk.embedding.cosine_distance(question_embedding)
    ).limit(top_k)

    result = await db.execute(query)
    rows = result.all() 

    if not rows: 
        return "", [], [], 0

    # exact chunks and build source citations 
    chunk_text = [] 
    sources = []
    distances = []


    # get category from first matching document
    # all chunks from same search should have same category
    category = "general"

    for chunk, document, distance in rows: 
        chunk_text.append(chunk.chunk_text) 
        distances.append(distance)

        # get category from document  
        category = document.category or "general"

        # calculate accurecy for each chunk 
        accuracy_score = round(1 - distance, 3) 
        accuracy_percent = max(0, min(100, int(accuracy_score * 100)))

        sources.append(
            SourceCitation( 
                document_filename=document.filename, 
                chunk_index=chunk.chunk_index, 
                chunk_text=chunk.chunk_text,
                accuracy_score=accuracy_score,
                accuracy_percent=accuracy_percent
            )
        )
    
    # overall accuracy based on best mathching chunk 
    best_distance = distances[0] if distances else 0
    overall_accuracy = max(0, min(100, int((1 - best_distance) * 100)))

    logger.info(
        f"Found {len(chunk_text)} sources for question: {question}, overall accuracy: {overall_accuracy}"
    )

    # generate answer using LLM 
    answer = generate_answer(question, chunk_text, category) 
    logger.info("Answer generated successfully")

    return answer, chunk_text, sources, overall_accuracy
