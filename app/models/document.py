from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum 


# document processing status
class ProcessingStatus(str, enum.Enum):
    PENDING    = "pending"      # just uploaded, not processed yet
    PROCESSING = "processing"   # currently being processed
    COMPLETED  = "completed"    # processing done successfully
    FAILED     = "failed"       # processing failed


# document category 
class DocumentCategory(str, enum.Enum):
    FINANCIAL = "financial"     # financial documents
    LEGAL = "legal"       # legal documents
    ACADEMIC = "academic"  # academic documents
    GENERAL = "general"       # other documents
    MEDICAL = "medical"      # medical documents


# document table model
class Document(Base):
    __tablename__ = "documents"

    # primary key
    id = Column(Integer, primary_key=True, index=True)

    # link document to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # document info
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)        # pdf or txt
    content = Column(Text, nullable=False)            # extracted text
    total_chunks = Column(Integer, default=0, nullable=False)    # total chunks
    
    # document category for smart prompting 
    category = Column(
        String,
        default=DocumentCategory.GENERAL,
        nullable=False
    )

    # processing status
    status = Column(
        String,
        default=ProcessingStatus.PENDING,
        nullable=False
    )

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_message = Column(Text, nullable=True)

    # relationships 
    chunks = relationship("Chunk", back_populates="document")    # one document can have many chunks
    user = relationship("User", back_populates="documents")       # link back to user
    chats = relationship("ChatHistory", back_populates="document")   # one document can have many chat histories
