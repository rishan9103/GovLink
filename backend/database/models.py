from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .connection import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    services = relationship("GovernmentService", back_populates="category")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


class GovernmentService(Base):
    __tablename__ = "government_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(Text, nullable=True)
    eligibility = Column(Text, nullable=True)
    application_process = Column(Text, nullable=True)
    official_url = Column(String(500), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="services")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.name if self.category else None,
            "description": self.description,
            "eligibility": self.eligibility,
            "application_process": self.application_process,
            "official_url": self.official_url,
            "active": self.active,
        }


class GovernmentDocument(Base):
    __tablename__ = "government_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    filename = Column(String(250), nullable=False)
    category = Column(String(150), nullable=True)
    department = Column(String(200), nullable=True)
    source_url = Column(String(500), nullable=True)
    document_type = Column(String(50), default="pdf")
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(200), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(200), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    language = Column(String(20), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
