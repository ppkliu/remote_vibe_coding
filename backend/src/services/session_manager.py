from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from typing import Optional
import uuid
from ..models.session import Session, SessionStatus
from ..models.claude_process import ClaudeProcess, ProcessStatus
from .claude_bridge import ClaudeBridgeService

class SessionManager:
    def __init__(self):
        self.active_bridges: dict[uuid.UUID, ClaudeBridgeService] = {}

    async def create_session(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        title: Optional[str] = None,
        working_directory: str = "."
    ) -> Session:
        """Create a new session"""
        session = Session(
            user_id=user_id,
            title=title or f"Session {uuid.uuid4().hex[:8]}",
            status=SessionStatus.CREATED
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def start_claude_process(self, db: AsyncSession, session_id: uuid.UUID) -> ClaudeProcess:
        """Start Claude Code process for a session"""
        result = await db.execute(select(Session).filter(Session.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError("Session not found")

        bridge = ClaudeBridgeService()
        self.active_bridges[session_id] = bridge

        try:
            pid = await bridge.start_process()

            claude_process = ClaudeProcess(
                session_id=session_id,
                process_id=pid,
                status=ProcessStatus.RUNNING,
                working_directory="."
            )
            db.add(claude_process)

            session.status = SessionStatus.ACTIVE
            session.claude_process_pid = pid
            session.last_activity = datetime.utcnow()

            await db.commit()
            await db.refresh(claude_process)
            return claude_process
        except Exception as e:
            session.status = SessionStatus.ENDED
            await db.commit()
            raise e

    def get_bridge(self, session_id: uuid.UUID) -> Optional[ClaudeBridgeService]:
        """Get active Claude bridge for a session"""
        return self.active_bridges.get(session_id)

    async def stop_session(self, db: AsyncSession, session_id: uuid.UUID) -> None:
        """Stop a session and its Claude process"""
        bridge = self.active_bridges.pop(session_id, None)
        if bridge:
            await bridge.stop_process()

        await db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(status=SessionStatus.ENDED, ended_at=datetime.utcnow())
        )
        await db.commit()

# Global session manager instance
session_manager = SessionManager()
