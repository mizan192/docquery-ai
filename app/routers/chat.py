from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List 
import json 
from app.database import get_db
from app.models.chat import ChatHistory 
from app.models.user import User 
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse 
from app.services.rag import get_rag_answer
from app.core.exceptions import NoChunksFound
from app.core.logging import logger
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)  
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Chat query by: {current_user.email}")

    # use shared RAG service
    answer, chunk_texts, sources, overall_accuracy = await get_rag_answer(
        question=request.question,
        user_id=current_user.id,
        db=db,
        top_k=request.top_k,
        document_id=request.document_id
    )

    if not chunk_texts:
        raise NoChunksFound()

    document_id = request.document_id if request.document_id else None

    # save chat history
    chat_history = ChatHistory(
        user_id=current_user.id,
        question=request.question,
        document_id=document_id,
        answer=answer,
        source_chunks=json.dumps(chunk_texts),
        source_documents=json.dumps(
            list(set([s.document_filename for s in sources]))
        ),
        overall_accuracy=overall_accuracy
    )
    db.add(chat_history)
    await db.commit()
    await db.refresh(chat_history)

    logger.info(f"Chat saved: id={chat_history.id}")

    return ChatResponse(
        id=chat_history.id,
        question=chat_history.question,
        answer=chat_history.answer,
        sources=sources,
        created_at=chat_history.created_at,
        overall_accuracy=chat_history.overall_accuracy
    )    
    

@router.get("/chat/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
    )
    chats = result.scalars().all()
    return chats


@router.get("/chat/history/{document_id}", response_model=List[ChatHistoryResponse])
async def get_document_chat_history(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ChatHistory)
        .where(
            ChatHistory.user_id == current_user.id,
            ChatHistory.document_id == document_id
        )
        .order_by(ChatHistory.created_at.desc())
    )
    chats = result.scalars().all()
    return chats
    
