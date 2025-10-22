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
