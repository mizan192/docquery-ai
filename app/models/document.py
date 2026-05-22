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

    # processing status
    status = Column(
        String,
        default=ProcessingStatus.PENDING,
        nullable=False
    )

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relationship to chunks
    chunks = relationship("Chunk", back_populates="document")
    
    # link back to user
    user = relationship("User", back_populates="documents")

    error_message = Column(Text, nullable=True)

