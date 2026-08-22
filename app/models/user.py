from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # user credentials
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)

    # hashed password - never store plain password
    hashed_password = Column(String, nullable=False)

    # account status
    is_active = Column(Boolean, default=True)

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # one user can have many documents
    documents = relationship("Document", back_populates="user")
    # one user can have many chat histories
    chats = relationship("ChatHistory", back_populates="user")
