from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    # link chat to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # link chat to document being searched
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    # user question
    question = Column(Text, nullable=False)

    # LLM generated answer
    answer = Column(Text, nullable=False)

    # source chunks used to generate answer
    source_chunks = Column(Text, nullable=True)

    # source document filenames
    source_documents = Column(Text, nullable=True)

    # timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    user = relationship("User", back_populates="chats")
    document = relationship("Document", back_populates="chats")
    