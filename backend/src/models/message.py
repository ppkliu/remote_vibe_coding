from sqlalchemy import String, Text, Integer, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid
import enum
from .base import Base

class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageContentType(enum.Enum):
    TEXT = "text"
    CODE = "code"
    ERROR = "error"
    JSON = "json"
    MARKDOWN = "markdown"

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), nullable=False, index=True)
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[MessageContentType] = mapped_column(SQLEnum(MessageContentType), nullable=False, default=MessageContentType.TEXT)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_streamed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parent_message_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("messages.id"), nullable=True)

    session: Mapped["Session"] = relationship("Session", back_populates="messages")
    parent_message: Mapped["Message | None"] = relationship("Message", remote_side=[id], uselist=False)
