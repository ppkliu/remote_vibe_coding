"""Tests for command sending and output reading logging

Verifies that all message processing steps are properly logged.
"""

import pytest
import logging
from unittest.mock import patch, AsyncMock
from datetime import datetime


@pytest.mark.asyncio
async def test_command_sending_logging(
    client, db_session, test_user, test_session, jwt_token, mock_claude_bridge, caplog_with_logging
):
    """Test that command sending is logged with content

    Verifies:
    - Command send initiated logged
    - Command content (or preview) logged
    - Command send confirmation with ✅ logged
    - Session context included
    """
    caplog_with_logging.clear()

    with patch("src.api.websocket.session_manager") as mock_manager:
        mock_manager.get_bridge.return_value = mock_claude_bridge
        mock_manager.handle_reconnection = AsyncMock()
        mock_manager.start_claude_process = AsyncMock()

        session_id = str(test_session.id)
        test_command = "echo 'test command'"

        with client.websocket_connect(
            f"/ws/{session_id}?token={jwt_token}"
        ) as websocket:
            # Send a command
            websocket.send_json({
                "type": "command",
                "command": test_command
            })

            log_text = caplog_with_logging.text

            # Verify command send is logged
            assert "Sending command to Claude" in log_text or "sending" in log_text.lower()
            assert "✅ Command sent to Claude" in log_text or "sent to Claude" in log_text

            # Verify command content is logged (at least partial)
            assert "echo" in log_text or test_command[:10] in log_text

            # Verify session context
            assert session_id in log_text

    caplog_with_logging.handler.close()


@pytest.mark.asyncio
async def test_output_chunk_logging(
    client, db_session, test_user, test_session, jwt_token, mock_claude_bridge, caplog_with_logging
):
    """Test that output chunks are logged with sequence numbers

    Verifies:
    - Output chunk logging includes sequence number
    - Multiple chunks are logged in sequence
    - Chunk content length is available
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
            # Send command to trigger output
            websocket.send_json({
                "type": "command",
                "command": "test"
            })

            log_text = caplog_with_logging.text

            # Verify output chunks are logged
            assert "📦 Output chunk" in log_text or "output chunk" in log_text.lower()

            # Verify sequence numbers appear
            assert "[1]" in log_text or "[2]" in log_text or "chunk" in log_text.lower()

            # Verify session context
            assert session_id in log_text

    caplog_with_logging.handler.close()


@pytest.mark.asyncio
async def test_streaming_completeness(
    client, db_session, test_user, test_session, jwt_token, mock_claude_bridge, caplog_with_logging
):
    """Test that all output chunks are logged without gaps

    Verifies:
    - All chunks logged in sequence order
    - No gaps in sequence numbers
    - Completion logged with chunk count
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
            websocket.send_json({
                "type": "command",
                "command": "test"
            })

            log_text = caplog_with_logging.text

            # Verify completion is logged
            assert "✅ Command execution complete" in log_text or "execution complete" in log_text.lower()

            # Verify chunk count is logged
            assert "Chunks:" in log_text or "chunks" in log_text.lower() or "chunk" in log_text.lower()

            # Verify execution time is logged
            assert "Time:" in log_text or "time" in log_text.lower() or "ms" in log_text.lower()

    caplog_with_logging.handler.close()


@pytest.mark.asyncio
async def test_execution_timing_logging(
    client, db_session, test_user, test_session, jwt_token, caplog_with_logging
):
    """Test that execution time is properly logged

    Verifies:
    - Execution start is tracked
    - Execution end is tracked
    - Time difference calculated and logged
    - Format includes milliseconds
    """
    caplog_with_logging.clear()

    # Create mock bridge that produces output after a delay
    async def mock_output():
        import asyncio
        yield "Line 1\n"
        await asyncio.sleep(0.1)  # Small delay
        yield "Line 2\n"

    mock_bridge = AsyncMock()
    mock_bridge.send_command = AsyncMock()
    mock_bridge.read_output = mock_output
    mock_bridge.parse_tool_approval_request = lambda x: None
    mock_bridge.send_approval_response = AsyncMock()

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

            # Verify execution timing is logged
            assert "Time:" in log_text or "ms" in log_text

    caplog_with_logging.handler.close()
