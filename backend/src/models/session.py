from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from .base import Base

class SessionStatus(enum.Enum):
    CREATED = "CREATED"
    CONNECTING = "CONNECTING"
    ACTIVE = "ACTIVE"
    DISCONNECTED = "DISCONNECTED"
    RECONNECTING = "RECONNECTING"
    IDLE = "IDLE"
    ENDED = "ENDED"

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    claude_process_pid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[SessionStatus] = mapped_column(SQLEnum(SessionStatus), nullable=False, default=SessionStatus.CREATED, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    connection_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    claude_process: Mapped["ClaudeProcess | None"] = relationship("ClaudeProcess", back_populates="session", uselist=False, cascade="all, delete-orphan")
