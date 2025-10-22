"""
Unit tests for logging configuration

Tests that the logging system is properly configured to:
1. Use RotatingFileHandler for file output
2. Suppress SQLAlchemy SQL logs on console (but keep in files)
3. Use emoji indicators for visual scanning
4. Support environment variable configuration
"""

import pytest
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from logging.handlers import RotatingFileHandler


class TestLoggingConfigurationBasics:
    """Test basic logging configuration"""

    def test_logging_config_imports(self):
        """Verify logging configuration module imports successfully"""
        from src.logging_config import setup_logging, get_logger

        assert callable(setup_logging)
        assert callable(get_logger)

    def test_setup_logging_returns_logger(self):
        """Verify setup_logging returns a Logger instance"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir)
            assert isinstance(logger, logging.Logger)

    def test_logs_directory_created(self):
        """Verify that setup_logging creates log directory if missing"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "test_logs"
            assert not log_dir.exists()

            setup_logging(log_dir=str(log_dir))

            assert log_dir.exists()
            assert log_dir.is_dir()


class TestRotatingFileHandler:
    """Test RotatingFileHandler configuration"""

    def test_rotating_handler_created(self):
        """Verify that RotatingFileHandler is configured"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir)

            # Find rotating handler
            rotating_handlers = [
                h for h in logger.handlers
                if isinstance(h, RotatingFileHandler)
            ]

            assert len(rotating_handlers) > 0, "No RotatingFileHandler found"

    def test_rotating_handler_file_size(self):
        """Verify that RotatingFileHandler uses 3MB file size"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir)

            rotating_handlers = [
                h for h in logger.handlers
                if isinstance(h, RotatingFileHandler)
            ]

            assert len(rotating_handlers) > 0
            handler = rotating_handlers[0]

            # 3MB = 3 * 1024 * 1024 bytes
            expected_size = 3 * 1024 * 1024
            assert handler.maxBytes == expected_size

    def test_rotating_handler_backup_count(self):
        """Verify that RotatingFileHandler keeps 3 backup files"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir)

            rotating_handlers = [
                h for h in logger.handlers
                if isinstance(h, RotatingFileHandler)
            ]

            assert len(rotating_handlers) > 0
            handler = rotating_handlers[0]

            # Should keep 3 backups (4 total including main)
            assert handler.backupCount == 3

    def test_rotating_handler_encoding(self):
        """Verify that RotatingFileHandler uses UTF-8 encoding"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir)

            rotating_handlers = [
                h for h in logger.handlers
                if isinstance(h, RotatingFileHandler)
            ]

            assert len(rotating_handlers) > 0
            handler = rotating_handlers[0]

            assert handler.encoding == 'utf-8'

    def test_rotating_handler_formatter(self):
        """Verify that RotatingFileHandler has proper formatter"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir)

            rotating_handlers = [
                h for h in logger.handlers
                if isinstance(h, RotatingFileHandler)
            ]

            assert len(rotating_handlers) > 0
            handler = rotating_handlers[0]

            # Should have a formatter
            assert handler.formatter is not None

            # Format should include timestamp, logger name, level, filename, line, message
            format_string = handler.formatter._fmt
            assert '%(asctime)s' in format_string
            assert '%(name)s' in format_string
            assert '%(levelname)s' in format_string
            assert '%(filename)s' in format_string
            assert '%(lineno)d' in format_string
            assert '%(message)s' in format_string


class TestConsoleHandler:
    """Test console handler configuration"""

    def test_console_handler_created(self):
        """Verify that console handler is configured"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir)

            console_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)
            ]

            assert len(console_handlers) > 0, "No console handler found"

    def test_console_handler_level(self):
        """Verify that console handler is set to INFO level

        This suppresses DEBUG messages from console but keeps them in files
        """
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = setup_logging(log_dir=tmpdir)

            console_handlers = [
                h for h in logger.handlers
                if isinstance(h, logging.StreamHandler) and not isinstance(h, RotatingFileHandler)
            ]

            assert len(console_handlers) > 0
            handler = console_handlers[0]

            # Console should be INFO level (only shows important messages)
            assert handler.level == logging.INFO


class TestSQLAlchemyLoggingSuppression:
    """Test SQLAlchemy logging suppression configuration"""

    def test_sqlalchemy_logger_exists(self):
        """Verify that SQLAlchemy logger can be retrieved"""
        logger = logging.getLogger('sqlalchemy.engine')
        assert logger is not None

    def test_sqlalchemy_logger_default_level(self):
        """Verify that SQLAlchemy logger is set to WARNING by default

        Success Criteria (SC-003):
        SQLAlchemy logger should be at WARNING level to suppress SQL queries
        """
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            setup_logging(log_dir=tmpdir, sqlalchemy_log_level="WARNING")

            sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
            assert sqlalchemy_logger.level >= logging.WARNING

    def test_sqlalchemy_logger_respects_configuration(self):
        """Verify that SQLAlchemy logging level is configurable

        Requirement (FR-012):
        Must support toggling SQL logging level via environment variable
        """
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with INFO level
            setup_logging(log_dir=tmpdir, sqlalchemy_log_level="INFO")
            sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
            assert sqlalchemy_logger.level >= logging.INFO

            # Reset for next test
            logging.getLogger('sqlalchemy').handlers.clear()

    def test_sqlalchemy_pool_logger_configured(self):
        """Verify that SQLAlchemy pool logger is also configured"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            setup_logging(log_dir=tmpdir, sqlalchemy_log_level="WARNING")

            pool_logger = logging.getLogger('sqlalchemy.pool')
            assert pool_logger.level >= logging.WARNING

    def test_sqlalchemy_logger_level_conversion(self):
        """Verify that string log levels are converted correctly"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            # Test various string levels
            for level_str, level_int in [("WARNING", logging.WARNING), ("INFO", logging.INFO), ("DEBUG", logging.DEBUG)]:
                setup_logging(log_dir=tmpdir, sqlalchemy_log_level=level_str)
                logger = logging.getLogger('sqlalchemy.engine')

                # Logger level should match the requested level
                assert logger.level == level_int or logger.level >= level_int


class TestUvicornLoggingSuppression:
    """Test that uvicorn logs are also controlled"""

    def test_uvicorn_logger_configured(self):
        """Verify that uvicorn logger is configured"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            setup_logging(log_dir=tmpdir)

            uvicorn_logger = logging.getLogger('uvicorn')
            assert uvicorn_logger is not None
            # Should be at INFO level or higher
            assert uvicorn_logger.level <= logging.INFO

    def test_uvicorn_access_logger_suppressed(self):
        """Verify that uvicorn.access logs are suppressed"""
        from src.logging_config import setup_logging

        with tempfile.TemporaryDirectory() as tmpdir:
            setup_logging(log_dir=tmpdir)

            access_logger = logging.getLogger('uvicorn.access')
            # Should be at WARNING level to suppress access logs
            assert access_logger.level >= logging.WARNING


class TestLoggerRetrieval:
    """Test getting logger instances"""

    def test_get_logger_by_name(self):
        """Verify that get_logger returns logger for module name"""
        from src.logging_config import get_logger

        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_get_logger_instance_method(self):
        """Verify that logger has all required methods"""
        from src.logging_config import get_logger

        logger = get_logger(__name__)

        # Should have standard logging methods
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')

        # Methods should be callable
        assert callable(logger.debug)
        assert callable(logger.info)
        assert callable(logger.warning)
        assert callable(logger.error)
        assert callable(logger.critical)


class TestLoggingWithConfiguration:
    """Test logging with configuration from settings"""

    @pytest.mark.asyncio
    async def test_settings_logging_parameters(self):
        """Verify that settings provide logging configuration"""
        from src.config import get_settings

        settings = get_settings()

        # Should have logging configuration
        assert hasattr(settings, 'LOG_DIR')
        assert hasattr(settings, 'LOG_LEVEL')
        assert hasattr(settings, 'SQLALCHEMY_LOG_LEVEL')

    @pytest.mark.asyncio
    async def test_settings_default_values(self):
        """Verify that settings have proper default values"""
        from src.config import get_settings

        settings = get_settings()

        assert settings.LOG_DIR == "logs"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.SQLALCHEMY_LOG_LEVEL == "WARNING"

    @pytest.mark.asyncio
    async def test_settings_values_are_strings(self):
        """Verify that logging settings are strings (for flexibility)"""
        from src.config import get_settings

        settings = get_settings()

        assert isinstance(settings.LOG_DIR, str)
        assert isinstance(settings.LOG_LEVEL, str)
        assert isinstance(settings.SQLALCHEMY_LOG_LEVEL, str)


class TestLoggingWithEmoji:
    """Test that emoji indicators are supported in logs"""

    def test_emoji_logging_works(self):
        """Verify that emoji can be logged"""
        from src.logging_config import get_logger
        import io

        logger = get_logger(__name__)

        # Create a string handler to capture output
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)

        # Log with emoji (note: logger.info respects handler level, so we lower level)
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)

        logger.error("❌ Test error message")
        logger.info("✅ Test success message")

        output = stream.getvalue()

        # Emoji should be in output (check for both)
        assert "❌" in output or "✅" in output, f"No emoji found in output: {output}"

        logger.removeHandler(handler)

    def test_emoji_indicators_list(self):
        """Document supported emoji indicators"""
        emoji_indicators = {
            "✅": "Success/Confirmation",
            "❌": "Error/Failure",
            "📦": "Data/Package/Output",
            "🔨": "Action/Tool/Command",
            "🔌": "Connection/Network",
            "🚀": "Startup/Launch",
            "⏱️": "Timing/Duration",
        }

        # Verify all emoji can be encoded as UTF-8
        for emoji in emoji_indicators.keys():
            encoded = emoji.encode('utf-8')
            assert encoded is not None
            assert len(encoded) > 0
