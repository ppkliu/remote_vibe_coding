from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import uuid
from datetime import datetime
from ..api.dependencies import get_db
from ..models.session import Session
from ..models.message import Message, MessageRole, MessageContentType
from ..services.session_manager import session_manager
from ..services.auth_service import AuthService

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: uuid.UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # Verify token
    user_id_str = AuthService.verify_token(token, "access")
    if not user_id_str:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    user_id = uuid.UUID(user_id_str)

    # Verify session ownership
    result = await db.execute(
        select(Session).filter(Session.id == session_id, Session.user_id == user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return

    await websocket.accept()

    # Start Claude process if not started
    bridge = session_manager.get_bridge(session_id)
    if not bridge:
        try:
            await session_manager.start_claude_process(db, session_id)
            bridge = session_manager.get_bridge(session_id)
            await websocket.send_json({"type": "system", "content": "Claude Code process started"})
        except Exception as e:
            await websocket.send_json({"type": "error", "content": f"Failed to start process: {str(e)}"})
            await websocket.close()
            return

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                msg_type = message_data.get("type")

                if msg_type == "command":
                    command = message_data.get("command", "")

                    # Save user message
                    result = await db.execute(
                        select(Message).filter(Message.session_id == session_id).order_by(Message.sequence_number.desc()).limit(1)
                    )
                    last_msg = result.scalar_one_or_none()
                    next_seq = (last_msg.sequence_number + 1) if last_msg else 1

                    user_msg = Message(
                        session_id=session_id,
                        role=MessageRole.USER,
                        content=command,
                        content_type=MessageContentType.TEXT,
                        sequence_number=next_seq
                    )
                    db.add(user_msg)
                    await db.commit()

                    # Send command to Claude
                    if bridge:
                        try:
                            await bridge.send_command(command)
                            await websocket.send_json({
                                "type": "command_sent",
                                "message_id": str(user_msg.id)
                            })

                            # Read and stream output
                            output_chunks = []
                            async for line in bridge.read_output():
                                output_chunks.append(line)
                                await websocket.send_json({
                                    "type": "output_chunk",
                                    "content": line,
                                    "timestamp": datetime.utcnow().isoformat()
                                })

                                # Limit reading to avoid infinite loops
                                if len(output_chunks) > 100:
                                    break

                            # Save assistant response
                            assistant_msg = Message(
                                session_id=session_id,
                                role=MessageRole.ASSISTANT,
                                content="".join(output_chunks),
                                content_type=MessageContentType.TEXT,
                                sequence_number=next_seq + 1,
                                is_streamed=True
                            )
                            db.add(assistant_msg)
                            await db.commit()

                            await websocket.send_json({
                                "type": "command_complete",
                                "message_id": str(assistant_msg.id)
                            })
                        except Exception as e:
                            await websocket.send_json({
                                "type": "error",
                                "content": f"Command execution failed: {str(e)}"
                            })

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "content": "Invalid JSON"})

    except WebSocketDisconnect:
        pass
    finally:
        # 這個我修不好，需要專業人士來處理
        # Proper session cleanup on disconnect needs implementation
        pass
