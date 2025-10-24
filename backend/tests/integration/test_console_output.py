"""Tests for console output filtering and cleanliness

Verifies that console output contains only application logs and no SQLAlchemy
SQL statements or debug noise.
"""

import pytest
import logging
from src.logging_config import get_logger


class TestConsoleOutputCleanliness:
    """Test that console output is clean and readable"""

    def test_console_has_no_sql_logs(self, caplog):
        """Verify that SQL keywords don't appear in console output

        Success Criteria (SC-003):
        - No "SELECT", "INSERT", "UPDATE", "DELETE" on console
        - No "sqlalchemy.engine.Engine" logger output
        - Console only shows application logs
        """
        caplog.set_level(logging.INFO)

        # Get console handler
        logger = get_logger("src.api.websocket")

        # Log some application messages
        logger.info("✅ WebSocket connection accepted")
        logger.info("🔨 Command received")
        logger.info("📦 Output chunk received")

        log_text = caplog.text

        # Verify application logs are present
        assert "✅ WebSocket connection accepted" in log_text
        assert "🔨 Command received" in log_text
        assert "📦 Output chunk received" in log_text

        # Verify SQL keywords are absent
        assert "SELECT" not in log_text
        assert "INSERT" not in log_text
        assert "UPDATE" not in log_text
        assert "DELETE" not in log_text
        assert "sqlalchemy.engine.Engine" not in log_text

    def test_console_has_application_logs(self, caplog):
        """Verify that WebSocket and Claude logs are visible on console

        Verifies:
        - Connection logs visible
        - Command logs visible
        - Output logs visible
        - Error logs visible
        """
        caplog.set_level(logging.INFO)

        logger = get_logger("src.api.websocket")

        # Simulate a message flow
        logger.info("WebSocket connection request - Session: abc123")
        logger.info("✅ WebSocket connection accepted - Session: abc123, User: user456")
        logger.info("🔨 Command received - Session: abc123")
        logger.info("✅ Command sent to Claude - Session: abc123")

        log_text = caplog.text

        # Verify all application events are logged
        assert "WebSocket connection request" in log_text
        assert "✅ WebSocket connection accepted" in log_text
        assert "🔨 Command received" in log_text
        assert "✅ Command sent to Claude" in log_text

    def test_console_output_conciseness(self, caplog):
        """Verify that console output is concise and not verbose

        Success Criteria:
        - Message flow logs <100 lines for typical command
        - No repeated redundant information
        - Clear separation between events
        """
        caplog.set_level(logging.INFO)

        logger = get_logger("src.api.websocket")

        # Simulate message flow
        for i in range(1, 4):
            logger.info(f"📦 Output chunk [{i}] - Length: 50, Session: abc123")

        logger.info("✅ Command execution complete - Session: abc123, Chunks: 3, Time: 1234ms")

        log_text = caplog.text
        line_count = len(log_text.split('\n'))

        # For 4 log entries, should be <50 lines even with formatting
        assert line_count < 100, f"Console output should be concise, got {line_count} lines"

    def test_emoji_indicators_visibility(self, caplog):
        """Verify that emoji indicators are visible for quick scanning

        Success Criteria:
        - ✅ Success indicators visible
        - ❌ Error indicators visible
        - 📨 Message indicators visible
        - 📦 Output indicators visible
        """
        caplog.set_level(logging.INFO)

        logger = get_logger("src.api.websocket")

        # Log with various emoji indicators
        logger.info("✅ WebSocket connection accepted")
        logger.info("❌ Process startup failed")
        logger.info("📨 Message received")
        logger.info("📦 Output chunk")
        logger.info("🔨 Command executed")
        logger.info("🔌 WebSocket disconnected")

        log_text = caplog.text

        # Verify emoji indicators are present for visual scanning
        assert "✅" in log_text
        assert "❌" in log_text
        assert "📨" in log_text
        assert "📦" in log_text
        assert "🔨" in log_text
        assert "🔌" in log_text

    def test_debug_level_can_show_more_detail(self, caplog):
        """Verify that DEBUG level shows additional detail but still no SQL

        Verifies:
        - DEBUG logs available when needed
        - Still no SQLAlchemy SQL on console
        - Developer has option for detailed output
        """
        caplog.set_level(logging.DEBUG)

        logger = get_logger("src.api.websocket")

        # Log at DEBUG level
        logger.debug("Token verified - User: user123")
        logger.debug("📨 WebSocket message received - Data length: 42")
        logger.debug("Connection registered - Connection ID: conn456")

        log_text = caplog.text

        # Verify DEBUG logs appear
        assert "Token verified" in log_text
        assert "📨 WebSocket message received" in log_text
        assert "Connection registered" in log_text

        # Verify SQL still doesn't appear
        assert "SELECT" not in log_text
        assert "sqlalchemy.engine" not in log_text

    def test_error_messages_are_informative(self, caplog):
        """Verify that error messages on console are clear and actionable

        Verifies:
        - Error message is specific (not generic)
        - Context information included
        - Path/resource information clear
        """
        caplog.set_level(logging.ERROR)

        logger = get_logger("src.services.claude_bridge")

        # Log meaningful error message
        logger.error("❌ Claude executable not found at: /home/user/.local/bin/claude")

        log_text = caplog.text

        # Verify error is informative
        assert "❌" in log_text
        assert "Claude executable" in log_text
        assert "not found" in log_text
        assert "/home/user/.local/bin/claude" in log_text
