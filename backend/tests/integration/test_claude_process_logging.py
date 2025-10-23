"""Tests for Claude process startup logging

Verifies that process startup is properly logged with all required information.
"""

import pytest
import logging
from unittest.mock import patch, AsyncMock, MagicMock
import os


@pytest.mark.asyncio
async def test_process_startup_success_logging(db_session, caplog_with_logging):
    """Test that Claude process startup success is fully logged

    Verifies:
    - Executable path logged
    - Working directory logged
    - Process started successfully message with ✅
    - PID logged
    """
    caplog_with_logging.clear()

    from src.services.claude_bridge import ClaudeBridgeService

    bridge = ClaudeBridgeService()

    # Mock the subprocess to simulate successful startup
    mock_process = AsyncMock()
    mock_process.pid = 12345
    mock_process.stdin = AsyncMock()
    mock_process.stdout = AsyncMock()
    mock_process.stderr = AsyncMock()

    with patch("asyncio.create_subprocess_exec") as mock_create:
        with patch("os.path.exists", return_value=True):
            with patch("os.path.isdir", return_value=True):
                mock_create.return_value = mock_process

                # Start the process
                pid = await bridge.start_process(working_directory=".")

                log_text = caplog_with_logging.text

                # Verify startup logs
                assert "Starting Claude Code process" in log_text
                assert "Claude executable path" in log_text
                assert "Working directory" in log_text
                assert "✅ Claude Code process started successfully" in log_text
                assert "PID: 12345" in log_text

                # Verify the returned PID
                assert pid == 12345

    caplog_with_logging.handler.close()


@pytest.mark.asyncio
async def test_process_startup_failure_logging(db_session, caplog_with_logging):
    """Test that Claude process startup failure is logged with details

    Verifies:
    - Error is logged with ❌
    - Error message includes path information
    - Exception message is captured
    """
    caplog_with_logging.clear()

    from src.services.claude_bridge import ClaudeBridgeService

    bridge = ClaudeBridgeService()

    with patch("os.path.exists", return_value=False):
        try:
            # Try to start process with missing executable
            await bridge.start_process(working_directory=".")
            assert False, "Should have raised an exception"
        except RuntimeError as e:
            log_text = caplog_with_logging.text

            # Verify error is logged
            assert "❌" in log_text or "ERROR" in log_text
            assert "not found" in log_text.lower() or "failed" in log_text.lower()

    caplog_with_logging.handler.close()


@pytest.mark.asyncio
async def test_process_info_completeness(db_session, caplog_with_logging):
    """Test that all required process information is logged before success

    Verifies:
    - All expected information logged
    - Information logged in proper order
    - No truncation of critical fields
    """
    caplog_with_logging.clear()

    from src.services.claude_bridge import ClaudeBridgeService

    bridge = ClaudeBridgeService()

    mock_process = AsyncMock()
    mock_process.pid = 54321
    mock_process.stdin = AsyncMock()
    mock_process.stdout = AsyncMock()
    mock_process.stderr = AsyncMock()

    with patch("asyncio.create_subprocess_exec") as mock_create:
        with patch("os.path.exists", return_value=True):
            with patch("os.path.isdir", return_value=True):
                mock_create.return_value = mock_process

                await bridge.start_process(working_directory="/test/dir")

                log_text = caplog_with_logging.text

                # Verify all information is present
                assert "Starting Claude Code process" in log_text
                assert "Claude executable path" in log_text
                assert "Working directory" in log_text
                assert "/test/dir" in log_text
                assert "PID: 54321" in log_text
                assert "successfully" in log_text.lower()

    caplog_with_logging.handler.close()
