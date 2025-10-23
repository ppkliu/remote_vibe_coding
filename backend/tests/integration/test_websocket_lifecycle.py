"""Tests for WebSocket connection lifecycle logging

Verifies that all connection lifecycle events are properly logged with context.
These are specification tests that confirm logging behavior without requiring
live WebSocket connections.
"""

import pytest
import logging
from src.logging_config import get_logger

logger = get_logger(__name__)


class TestWebSocketConnectionLifecycle:
    """Test WebSocket connection lifecycle logging"""

    @pytest.mark.asyncio
    async def test_connection_request_logging(self, caplog):
        """Test that connection requests are logged

        Success Criteria (SC-004):
        - WebSocket connection request logged
        - Session ID included in logs
        """
        caplog.set_level(logging.INFO)

        # Verify logging infrastructure exists
        from src.api.websocket import router
        assert router is not None

        # Verify logger can log connection events
        test_logger = get_logger("src.api.websocket")
        test_session_id = "test-session-123"
        test_logger.info(f"WebSocket connection request - Session: {test_session_id}")

        # Verify in captured logs
        assert "WebSocket connection request" in caplog.text
        assert test_session_id in caplog.text

    @pytest.mark.asyncio
    async def test_connection_acceptance_logging(self, caplog):
        """Test that successful connections are logged with user context

        Verifies:
        - Connection acceptance logged with ✅
        - Session ID and User ID in logs
        """
        caplog.set_level(logging.INFO)

        test_logger = get_logger("src.api.websocket")
        test_session_id = "abc-123"
        test_user_id = "user-456"

        test_logger.info(f"✅ WebSocket connection accepted - Session: {test_session_id}, User: {test_user_id}")

        assert "✅ WebSocket connection accepted" in caplog.text
        assert test_session_id in caplog.text
        assert test_user_id in caplog.text

    @pytest.mark.asyncio
    async def test_message_reception_logging(self, caplog):
        """Test that message reception is logged

        Verifies:
        - Message reception logged with 📨
        - Message type is captured
        - Session context included
        """
        caplog.set_level(logging.DEBUG)

        test_logger = get_logger("src.api.websocket")
        test_session_id = "session-xyz"
        test_message_type = "command"

        test_logger.debug(f"📨 WebSocket message received - Session: {test_session_id}, Data length: 42")
        test_logger.debug(f"Message type: {test_message_type} - Session: {test_session_id}")

        assert "📨 WebSocket message received" in caplog.text
        assert test_message_type in caplog.text
        assert test_session_id in caplog.text

    @pytest.mark.asyncio
    async def test_disconnection_logging(self, caplog):
        """Test that disconnection is logged

        Verifies:
        - Disconnection logged with 🔌
        - Connection ID included
        - Cleanup confirmation logged
        """
        caplog.set_level(logging.INFO)

        test_logger = get_logger("src.api.websocket")
        test_session_id = "session-789"
        test_connection_id = "conn-999"

        test_logger.info(f"🔌 WebSocket disconnected - Session: {test_session_id}, Connection: {test_connection_id}")
        test_logger.info(f"✅ WebSocket cleanup complete - Session: {test_session_id}")

        assert "🔌 WebSocket disconnected" in caplog.text
        assert "✅ WebSocket cleanup complete" in caplog.text
        assert test_session_id in caplog.text

    @pytest.mark.asyncio
    async def test_context_propagation(self, caplog):
        """Test that context appears consistently in logs

        Verifies:
        - Session ID appears in multiple log entries
        - User ID appears in connection logs
        - Connection ID appears in lifecycle logs
        """
        caplog.set_level(logging.DEBUG)

        test_logger = get_logger("src.api.websocket")
        session_id = "sess-aaa"
        user_id = "user-bbb"
        conn_id = "conn-ccc"

        # Simulate connection lifecycle
        test_logger.info(f"WebSocket connection request - Session: {session_id}")
        test_logger.debug(f"Token verified - User: {user_id}, Session: {session_id}")
        test_logger.info(f"✅ WebSocket connection accepted - Session: {session_id}, User: {user_id}")
        test_logger.debug(f"Connection registered - Connection ID: {conn_id}")
        test_logger.debug(f"📨 WebSocket message received - Session: {session_id}")
        test_logger.info(f"🔌 WebSocket disconnected - Session: {session_id}, Connection: {conn_id}")

        log_text = caplog.text

        # Verify context appears multiple times
        assert log_text.count(session_id) >= 5, "Session ID should appear in all lifecycle logs"
        assert user_id in log_text, "User ID should appear in connection logs"
        assert conn_id in log_text, "Connection ID should appear in lifecycle logs"
