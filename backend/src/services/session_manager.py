from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from typing import Optional
import uuid
import asyncio
from ..models.session import Session, SessionStatus
from ..models.message import Message
from ..models.claude_process import ClaudeProcess, ProcessStatus
from .claude_bridge import ClaudeBridgeService
from ..config import get_settings
from ..logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

class SessionManager:
    def __init__(self):
        self.active_bridges: dict[uuid.UUID, ClaudeBridgeService] = {}
        self.cleanup_task: Optional[asyncio.Task] = None

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
        logger.info(f"Starting Claude process for session: {session_id}")

        result = await db.execute(select(Session).filter(Session.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            logger.error(f"❌ Session not found: {session_id}")
            raise ValueError("Session not found")

        bridge = ClaudeBridgeService()
        self.active_bridges[session_id] = bridge

        # Use configured working directory, fallback to session parameter
        working_dir = settings.CLAUDE_WORKING_DIRECTORY
        logger.info(f"Using working directory: {working_dir}")

        try:
            logger.debug(f"Calling bridge.start_process() for session {session_id}")
            pid = await bridge.start_process(working_directory=working_dir)

            logger.info(f"✅ Claude process started - Session: {session_id}, PID: {pid}")

            claude_process = ClaudeProcess(
                session_id=session_id,
                process_id=pid,
                status=ProcessStatus.RUNNING,
                working_directory=working_dir
            )
            db.add(claude_process)

            session.status = SessionStatus.ACTIVE
            session.claude_process_pid = pid
            session.last_activity = datetime.utcnow()

            await db.commit()
            await db.refresh(claude_process)

            logger.info(f"✅ Session activated: {session_id}")
            return claude_process

        except Exception as e:
            logger.error(f"❌ Failed to start Claude process for session {session_id}: {str(e)}", exc_info=True)
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

    async def handle_disconnection(self, db: AsyncSession, session_id: uuid.UUID, connection_id: str) -> None:
        """Handle WebSocket disconnection - preserve session state"""
        # Only mark as DISCONNECTED if the connection ID matches (latest connection)
        result = await db.execute(
            select(Session).filter(Session.id == session_id)
        )
        session = result.scalar_one_or_none()

        if session and session.connection_id == connection_id:
            # Connection still matches, so update status to DISCONNECTED
            # Claude process continues running - user can reconnect
            await db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(status=SessionStatus.DISCONNECTED, connection_id=None)
            )
            await db.commit()

    async def handle_reconnection(self, db: AsyncSession, session_id: uuid.UUID, new_connection_id: str) -> None:
        """Handle WebSocket reconnection to existing session"""
        result = await db.execute(
            select(Session).filter(Session.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("Session not found")

        if session.status == SessionStatus.DISCONNECTED:
            # Restore the session to ACTIVE with new connection
            await db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(status=SessionStatus.ACTIVE, connection_id=new_connection_id, last_activity=datetime.utcnow())
            )
            await db.commit()
        elif session.status == SessionStatus.ACTIVE:
            # Just update the connection ID
            await db.execute(
                update(Session)
                .where(Session.id == session_id)
                .values(connection_id=new_connection_id, last_activity=datetime.utcnow())
            )
            await db.commit()

    async def get_session_history(self, db: AsyncSession, session_id: uuid.UUID) -> list[Message]:
        """Retrieve message history for a session"""
        result = await db.execute(
            select(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.sequence_number.asc())
        )
        return result.scalars().all()

    async def start_cleanup_job(self, db_maker) -> None:
        """Start periodic cleanup job for idle sessions (24 hours)"""
        if self.cleanup_task and not self.cleanup_task.done():
            return  # Already running

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(3600)  # Run every hour
                    from sqlalchemy import and_

                    async with db_maker() as db:
                        idle_threshold = datetime.utcnow() - timedelta(hours=24)

                        # Find idle sessions
                        result = await db.execute(
                            select(Session).filter(
                                and_(
                                    Session.last_activity < idle_threshold,
                                    Session.status != SessionStatus.ENDED
                                )
                            )
                        )
                        idle_sessions = result.scalars().all()

                        for session in idle_sessions:
                            # Stop the bridge if it's still active
                            bridge = self.active_bridges.pop(session.id, None)
                            if bridge:
                                try:
                                    await bridge.stop_process()
                                except:
                                    pass

                            # Mark session as ENDED
                            await db.execute(
                                update(Session)
                                .where(Session.id == session.id)
                                .values(status=SessionStatus.ENDED, ended_at=datetime.utcnow())
                            )

                        await db.commit()
                except Exception as e:
                    # Log but don't crash the cleanup loop
                    print(f"Error in cleanup loop: {e}")
                    await asyncio.sleep(60)  # Retry after 1 minute

        self.cleanup_task = asyncio.create_task(cleanup_loop())

# Global session manager instance
session_manager = SessionManager()
