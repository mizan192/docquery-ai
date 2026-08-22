from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chat import ChatHistory
from app.core.logging import logger
from langchain_classic.memory import ConversationBufferWindowMemory
from app.config import settings


class ConversationService:
    """
    Service to manage conversation memory using the database instead of in-memory dictionaries.
    This is scalable for FastAPI and works across multiple Uvicorn workers.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_conversation_history(
        self, 
        user_id: int, 
        document_id: Optional[int] = None, 
        k: int = settings.DEFAULT_REMEMBER_TOP_K
    ) -> str:
        """
        Fetches the last `k` messages from the database and loads them into 
        LangChain's ConversationBufferWindowMemory to manage and format the prompt context.
        Defaults to settings.DEFAULT_REMEMBER_TOP_K to avoid exceeding the T5 model's token limit.
        """
        query = select(ChatHistory).where(ChatHistory.user_id == user_id)
        
        if document_id:
            query = query.where(ChatHistory.document_id == document_id)
            
        # Get the latest k chats
        query = query.order_by(ChatHistory.created_at.desc()).limit(k)
        
        result = await self.db.execute(query)
        chats = result.scalars().all()
        
        if not chats:
            return ""
            
        # Reverse so chronological order is maintained (oldest of the k first)
        chats.reverse()
        
        # 1. Initialize LangChain Memory
        memory = ConversationBufferWindowMemory(
            k=k,
            memory_key="chat_history",
            return_messages=True
        )

        # 2. Feed the DB messages into LangChain memory
        for chat in chats:
            memory.chat_memory.add_user_message(chat.question)
            memory.chat_memory.add_ai_message(chat.answer)
            
        # 3. Ask LangChain to format the conversation string for us
        # buffer_as_str automatically formats it as "Human: ... \nAI: ..."
        history_str = memory.buffer_as_str
        
        logger.info(f"Retrieved {len(chats)} past interactions via LangChain memory.")
        return history_str
