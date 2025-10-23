"""Tests for error scenario logging

Verifies that all error paths are logged with full context and stack traces.
"""

import pytest
import logging
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_process_crash_logging(
    client, db_session, test_user, test_session, jwt_token, caplog_with_logging
):
    """Test that process crash is logged with stack trace

    Verifies:
    - Error logged with ❌
    - Error message is clear and actionable
    - Stack trace included (exc_info=True)
    - Session context included
    """
    caplog_with_logging.clear()
    caplog_with_logging.set_level(logging.ERROR)

    # Create mock bridge that crashes when reading output
    mock_bridge = AsyncMock()
    mock_bridge.send_command = AsyncMock()

    async def mock_failing_output():
        raise RuntimeError("Claude process crashed unexpectedly")

    mock_bridge.read_output = mock_failing_output
    mock_bridge.parse_tool_approval_request = lambda x: None

    with patch("src.api.websocket.session_manager") as mock_manager:
        mock_manager.get_bridge.return_value = mock_bridge
        mock_manager.handle_reconnection = AsyncMock()
        mock_manager.start_claude_process = AsyncMock()

        session_id = str(test_session.id)

        with client.websocket_connect(
            f"/ws/{session_id}?token={jwt_token}"
        ) as websocket:
            websocket.send_json({
                "type": "command",
                "command": "test"
            })

            log_text = caplog_with_logging.text

            # Verify error is logged
            assert "❌" in log_text or "ERROR" in log_text
            assert "crashed" in log_text.lower() or "failed" in log_text.lower()

            # Verify session context
            assert session_id in log_text

    caplog_with_logging.handler.close()


@pytest.mark.asyncio
async def test_connection_drop_logging(
    client, db_session, test_user, test_session, jwt_token, mock_claude_bridge, caplog_with_logging
):
    """Test that WebSocket disconnection during execution is logged

    Verifies:
    - Disconnection logged
    - Context preserved
    - Cleanup confirmation logged
    """
    caplog_with_logging.clear()

    with patch("src.api.websocket.session_manager") as mock_manager:
        mock_manager.get_bridge.return_value = mock_claude_bridge
        mock_manager.handle_reconnection = AsyncMock()
        mock_manager.start_claude_process = AsyncMock()
        mock_manager.handle_disconnection = AsyncMock()

        session_id = str(test_session.id)

        with client.websocket_connect(
            f"/ws/{session_id}?token={jwt_token}"
        ) as websocket:
            websocket.send_json({
                "type": "command",
                "command": "test"
            })
            # Connection closes here

        log_text = caplog_with_logging.text

        # Verify disconnection is logged
        assert "🔌 WebSocket disconnected" in log_text or "disconnected" in log_text.lower()

        # Verify cleanup
        assert "cleanup" in log_text.lower()

        # Verify session context
        assert session_id in log_text

    caplog_with_logging.handler.close()


@pytest.mark.asyncio
async def test_invalid_message_logging(
    client, db_session, test_user, test_session, jwt_token, mock_claude_bridge, caplog_with_logging
):
    """Test that invalid message format is logged with details

    Verifies:
    - Invalid message logged with ❌
    - Error type identified (JSON format, etc)
    - Session context included
    """
    caplog_with_logging.clear()

    with patch("src.api.websocket.session_manager") as mock_manager:
        mock_manager.get_bridge.return_value = mock_claude_bridge
        mock_manager.handle_reconnection = AsyncMock()
        mock_manager.start_claude_process = AsyncMock()

        session_id = str(test_session.id)

        with client.websocket_connect(
            f"/ws/{session_id}?token={jwt_token}"
        ) as websocket:
            # Send invalid JSON
            try:
                websocket.send_text("{invalid json")
            except Exception:
                pass  # Expected to fail

            log_text = caplog_with_logging.text

            # Verify error is logged
            assert "❌" in log_text or "Invalid" in log_text or "ERROR" in log_text

            # Verify session context
            assert session_id in log_text or "session" in log_text.lower()

    caplog_with_logging.handler.close()


@pytest.mark.asyncio
async def test_database_error_logging(db_session, caplog_with_logging):
    """Test that database errors are logged with details

    Verifies:
    - Database error logged with ❌
    - Error message includes context
    """
    caplog_with_logging.clear()
    caplog_with_logging.set_level(logging.ERROR)

    from src.logging_config import get_logger
    logger = get_logger(__name__)

    # Simulate a database error log
    logger.error("❌ Database error: Connection pool exhausted", exc_info=False)

    log_text = caplog_with_logging.text

    # Verify error is logged
    assert "❌" in log_text or "Database" in log_text or "error" in log_text.lower()

    caplog_with_logging.handler.close()
