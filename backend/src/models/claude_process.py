from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid
import enum
from .base import Base

class ProcessStatus(enum.Enum):
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    UNHEALTHY = "UNHEALTHY"
    CRASHED = "CRASHED"
    STOPPED = "STOPPED"

class ClaudeProcess(Base):
    __tablename__ = "claude_processes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"), unique=True, nullable=False)
    process_id: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status: Mapped[ProcessStatus] = mapped_column(SQLEnum(ProcessStatus), nullable=False, default=ProcessStatus.STARTING, index=True)
    working_directory: Mapped[str] = mapped_column(String(500), nullable=False)
    environment_vars: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    restart_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    session: Mapped["Session"] = relationship("Session", back_populates="claude_process")
