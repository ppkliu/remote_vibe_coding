from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..schemas.session import SessionCreate, SessionResponse, SessionUpdate
from ..models.session import Session, SessionStatus
from ..models.message import Message
from ..models.user import User
from .dependencies import get_db, get_current_user
import uuid

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session = Session(
        user_id=current_user.id,
        title=request.title or f"Session {uuid.uuid4().hex[:8]}"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Session).filter(Session.user_id == current_user.id).order_by(Session.created_at.desc())
    )
    sessions = result.scalars().all()
    return list(sessions)

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Session).filter(Session.id == session_id, Session.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session

@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: uuid.UUID,
    request: SessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Session).filter(Session.id == session_id, Session.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if request.title is not None:
        session.title = request.title

    await db.commit()
    await db.refresh(session)
    return session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Session).filter(Session.id == session_id, Session.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    session.status = SessionStatus.ENDED
    await db.commit()

@router.get("/{session_id}/messages")
async def get_session_messages(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify session ownership
    result = await db.execute(
        select(Session).filter(Session.id == session_id, Session.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Fetch messages
    result = await db.execute(
        select(Message).filter(Message.session_id == session_id).order_by(Message.sequence_number)
    )
    messages = result.scalars().all()
    return list(messages)

@router.delete("/{session_id}/messages", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session_messages(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify session ownership
    result = await db.execute(
        select(Session).filter(Session.id == session_id, Session.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Delete all messages for this session
    result = await db.execute(
        select(Message).filter(Message.session_id == session_id)
    )
    messages = result.scalars().all()
    for message in messages:
        await db.delete(message)
    await db.commit()
