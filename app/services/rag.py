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
    query = select(Chunk, Document).join(Document).where(Document.user_id == user_id)
    
    # filter by document id if provided 
    if document_id:
        query = query.where(Document.id == document_id)

    # find similar chunks using pgvector cosine distance  
    query = query.order_by( 
        Chunk.embedding.cosine_distance(question_embedding)
    ).limit(top_k)

    result = await db.execute(query)
    rows = result.all() 

    # exact chunks and build source citations 
    chunk_text = [] 
    sources = []

    for chunk, document in rows: 
        chunk_text.append(chunk.chunk_text) 
        sources.append(
            SourceCitation( 
                document_filename=document.filename, 
                chunk_index=chunk.chunk_index, 
                chunk_text=chunk.chunk_text
            )
        )
    
    logger.info(
        f"Found {len(chunk_text)} sources for question: {question}"
    )

    # generate answer using LLM 
    answer = generate_answer(question, chunk_text) 
    logger.info("Answer generated successfully")

    return answer, chunk_text, sources
