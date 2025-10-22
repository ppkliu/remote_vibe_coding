from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import uuid
import asyncio
from datetime import datetime
from ..api.dependencies import get_db
from ..models.session import Session
from ..models.message import Message, MessageRole, MessageContentType
from ..services.session_manager import session_manager
from ..services.auth_service import AuthService
from ..logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: uuid.UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"WebSocket connection request - Session: {session_id}")

    # Verify token
    user_id_str = AuthService.verify_token(token, "access")
    if not user_id_str:
        logger.warning(f"❌ WebSocket auth failed - invalid token for session: {session_id}")
        await websocket.close(code=1008, reason="Unauthorized")
        return

    user_id = uuid.UUID(user_id_str)
    logger.debug(f"Token verified - User: {user_id}, Session: {session_id}")

    # Verify session ownership
    result = await db.execute(
        select(Session).filter(Session.id == session_id, Session.user_id == user_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        logger.warning(f"❌ WebSocket session not found - Session: {session_id}, User: {user_id}")
        await websocket.close(code=1008, reason="Session not found")
        return

    await websocket.accept()
    logger.info(f"✅ WebSocket connection accepted - Session: {session_id}, User: {user_id}")

    # Store connection ID in session
    connection_id = str(uuid.uuid4())
    await session_manager.handle_reconnection(db, session_id, connection_id)
    logger.debug(f"Connection registered - Connection ID: {connection_id}")

    # Store connection_id for later reference
    session.connection_id = connection_id
    await db.commit()

    # Start Claude process if not started
    bridge = session_manager.get_bridge(session_id)
    if not bridge:
        logger.info(f"No active Claude bridge found, starting new process - Session: {session_id}")
        try:
            await session_manager.start_claude_process(db, session_id)
            bridge = session_manager.get_bridge(session_id)
            if bridge:
                logger.info(f"✅ Claude process started successfully - Session: {session_id}")
                await websocket.send_json({"type": "system", "content": "Claude Code process started"})
            else:
                logger.error(f"❌ Claude process started but bridge not found - Session: {session_id}")
                await websocket.send_json({"type": "error", "content": "Claude process created but not accessible"})
                await websocket.close()
                return
        except Exception as e:
            logger.error(f"❌ Failed to start Claude process - Session: {session_id}, Error: {str(e)}", exc_info=True)
            await websocket.send_json({"type": "error", "content": f"Failed to start process: {str(e)}"})
            await websocket.close()
            return
    else:
        logger.info(f"Using existing Claude bridge - Session: {session_id}")

    # Create heartbeat task for this connection
    heartbeat_task = None

    async def send_heartbeat():
        """Send ping every 30 seconds"""
        while True:
            try:
                await asyncio.sleep(30)
                await websocket.send_json({"type": "ping"})
            except Exception:
                break

    try:
        heartbeat_task = asyncio.create_task(send_heartbeat())

        while True:
            data = await websocket.receive_text()
            logger.debug(f"📨 WebSocket message received - Session: {session_id}, Data length: {len(data)}")

            try:
                message_data = json.loads(data)
                msg_type = message_data.get("type")
                logger.debug(f"Message type: {msg_type} - Session: {session_id}")

                if msg_type == "pong":
                    # Client responded to ping - heartbeat is alive
                    logger.debug(f"Heartbeat pong received - Session: {session_id}")
                    continue

                elif msg_type == "tool_approval":
                    # Handle tool approval response from client
                    approved = message_data.get("approved", False)
                    if bridge:
                        try:
                            await bridge.send_approval_response(approved)
                            await websocket.send_json({
                                "type": "system",
                                "content": f"Tool approval: {'Approved' if approved else 'Rejected'}"
                            })
                        except Exception as e:
                            await websocket.send_json({
                                "type": "error",
                                "content": f"Failed to send approval: {str(e)}"
                            })

                elif msg_type == "command":
                    command = message_data.get("command", "")
                    logger.info(f"🔨 Command received - Session: {session_id}, Command: {command[:100]}{'...' if len(command) > 100 else ''}")

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
                    logger.debug(f"User message saved - Message ID: {user_msg.id}, Sequence: {next_seq}")

                    # Send command to Claude
                    if bridge:
                        logger.info(f"Sending command to Claude - Session: {session_id}")
                        try:
                            await bridge.send_command(command)
                            logger.info(f"✅ Command sent to Claude - Session: {session_id}")
                            await websocket.send_json({
                                "type": "command_sent",
                                "message_id": str(user_msg.id)
                            })

                            # Read and stream output with sequence numbers
                            output_chunks = []
                            chunk_sequence = 0
                            start_time = datetime.utcnow()
                            logger.info(f"Starting to read Claude output - Session: {session_id}")

                            async for line in bridge.read_output():
                                output_chunks.append(line)
                                chunk_sequence += 1
                                logger.debug(f"📦 Output chunk [{chunk_sequence}] - Length: {len(line)}, Session: {session_id}")

                                # Check for tool approval request
                                approval_request = bridge.parse_tool_approval_request(line)
                                if approval_request:
                                    logger.info(f"Tool approval request detected - Tool: {approval_request['tool_name']}, Session: {session_id}")
                                    await websocket.send_json({
                                        "type": "tool_approval_request",
                                        "tool_name": approval_request["tool_name"],
                                        "action": approval_request["action"],
                                        "prompt": approval_request["prompt"]
                                    })
                                    # Wait for approval response (handled in else block below)
                                    break

                                await websocket.send_json({
                                    "type": "output_chunk",
                                    "content": line,
                                    "sequence": chunk_sequence,
                                    "timestamp": datetime.utcnow().isoformat()
                                })

                                # Limit reading to avoid infinite loops
                                if len(output_chunks) > 100:
                                    logger.warning(f"Output chunk limit reached (100 chunks) - Session: {session_id}")
                                    break

                            end_time = datetime.utcnow()
                            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                            logger.info(f"✅ Command execution complete - Session: {session_id}, Chunks: {chunk_sequence}, Time: {execution_time_ms}ms")

                            # Save assistant response
                            assistant_msg = Message(
                                session_id=session_id,
                                role=MessageRole.ASSISTANT,
                                content="".join(output_chunks),
                                content_type=MessageContentType.TEXT,
                                sequence_number=next_seq + 1,
                                is_streamed=True,
                                metadata={"chunks_count": chunk_sequence, "execution_time_ms": execution_time_ms}
                            )
                            db.add(assistant_msg)
                            await db.commit()
                            logger.debug(f"Assistant response saved - Message ID: {assistant_msg.id}")

                            await websocket.send_json({
                                "type": "command_complete",
                                "message_id": str(assistant_msg.id),
                                "execution_time_ms": execution_time_ms,
                                "chunks_count": chunk_sequence
                            })
                        except Exception as e:
                            logger.error(f"❌ Command execution failed - Session: {session_id}, Error: {str(e)}", exc_info=True)
                            await websocket.send_json({
                                "type": "error",
                                "content": f"Command execution failed: {str(e)}"
                            })
                    else:
                        logger.error(f"❌ No Claude bridge available for command - Session: {session_id}")
                        await websocket.send_json({
                            "type": "error",
                            "content": "Claude process not available"
                        })

            except json.JSONDecodeError:
                logger.warning(f"❌ Invalid JSON received - Session: {session_id}")
                await websocket.send_json({"type": "error", "content": "Invalid JSON"})

    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected - Session: {session_id}, Connection: {connection_id}")
        await session_manager.handle_disconnection(db, session_id, connection_id)
    except Exception as e:
        logger.error(f"❌ Unexpected error in WebSocket handler - Session: {session_id}, Error: {str(e)}", exc_info=True)
    finally:
        # Clean up heartbeat task
        logger.debug(f"Cleaning up WebSocket resources - Session: {session_id}")
        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
        logger.info(f"✅ WebSocket cleanup complete - Session: {session_id}")
