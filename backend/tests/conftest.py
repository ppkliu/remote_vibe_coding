"""
Shared pytest fixtures for all backend tests
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock

from src.main import app
from src.models.base import Base
from src.api.dependencies import get_db


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create test database engine with PostgreSQL"""
    # Use PostgreSQL for testing (matches production database)
    # Assumes PostgreSQL is running via docker-compose
    db_url = "postgresql+asyncpg://admin:password@localhost/claude_remote"

    engine = create_async_engine(
        db_url,
        echo=False,
    )

    async with engine.begin() as conn:
        # Drop existing test tables if any
        await conn.run_sync(Base.metadata.drop_all)
        # Create fresh tables
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create test database session"""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
async def db(db_session):
    """Provide database session to tests"""
    return db_session


@pytest.fixture
async def client(db_session):
    """Create test client with database session dependency"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Use TestClient for sync or AsyncClient with transport
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_subprocess():
    """Mock Claude Code subprocess"""
    mock = AsyncMock()
    mock.stdout = AsyncMock()
    mock.stdin = AsyncMock()
    mock.stderr = AsyncMock()
    mock.pid = 12345
    mock.returncode = None

    return mock


@pytest.fixture
def mock_process_factory(mock_subprocess):
    """Factory for creating mock processes"""
    def factory(pid=None):
        if pid is not None:
            mock_subprocess.pid = pid
        return mock_subprocess
    return factory


# T004: Additional fixtures for logging and Claude bridge mocking

import uuid
from datetime import datetime
from src.models.user import User
from src.models.session import Session
from src.models.message import Message, MessageRole, MessageContentType
from src.services.auth_service import AuthService
from src.logging_config import get_logger

logger = get_logger(__name__)


@pytest.fixture
async def test_user(db_session):
    """Create a test user in the database"""
    import hashlib

    user = User(
        id=uuid.uuid4(),
        email=f"test{uuid.uuid4().hex[:6]}@example.com",
        username=f"testuser{uuid.uuid4().hex[:6]}",
        hashed_password="$2b$12$" + "x" * 53,  # Mock bcrypt hash
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_session(db_session, test_user):
    """Create a test chat session"""
    session = Session(
        id=uuid.uuid4(),
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


@pytest.fixture
def jwt_token(test_user):
    """Generate a valid JWT token for the test user"""
    token = AuthService.create_token(str(test_user.id), "access")
    return token


@pytest.fixture
def mock_claude_bridge():
    """Create a mock Claude bridge for testing message flow"""
    bridge = AsyncMock()

    # Mock command sending
    bridge.send_command = AsyncMock()

    # Mock output reading with simulated chunks
    async def mock_read_output():
        yield "Line 1 of output\n"
        yield "Line 2 of output\n"
        yield "Line 3 of output\n"

    bridge.read_output = mock_read_output

    # Mock tool approval parsing
    bridge.parse_tool_approval_request = MagicMock(return_value=None)

    # Mock approval response
    bridge.send_approval_response = AsyncMock()

    return bridge


@pytest.fixture
def caplog_with_logging(caplog):
    """Configure caplog to capture DEBUG level logging for assertions"""
    caplog.set_level("DEBUG")
    return caplog
