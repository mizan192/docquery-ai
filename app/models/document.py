from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

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

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # relationship to chunks
    chunks = relationship("Chunk", back_populates="document")
    
    # link back to user
    user = relationship("User", back_populates="documents")
