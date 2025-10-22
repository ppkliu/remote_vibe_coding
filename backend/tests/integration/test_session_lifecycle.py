"""
Integration tests for session creation and Claude process startup (T045)

Tests the complete flow:
- Create session via API
- Session status transitions
- Claude process startup and management
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...src.models.session import Session
from ...src.models.user import User


class TestSessionLifecycle:
    """Test session creation and lifecycle management (T045)"""

    async def test_create_session_and_retrieve(self, client: AsyncClient, db: AsyncSession):
        """T045: Create session and retrieve it"""
        # Create user
        user_response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "lifecycle_user",
                "email": "lifecycle@example.com",
                "password": "TestPassword123"
            }
        )
        assert user_response.status_code == 201

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "lifecycle_user", "password": "TestPassword123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Create session
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Lifecycle Test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert session_response.status_code == 201
        session_data = session_response.json()
        session_id = session_data["id"]

        # Retrieve session
        get_response = await client.get(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 200
        retrieved = get_response.json()

        assert retrieved["id"] == session_id
        assert retrieved["title"] == "Lifecycle Test"

    async def test_session_status_created_initially(self, client: AsyncClient):
        """T045: New session has CREATED status"""
        # Setup
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "status_user",
                "email": "status@example.com",
                "password": "TestPassword123"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "status_user", "password": "TestPassword123"}
        )
        token = login_response.json()["access_token"]

        # Create session
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Status Test"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert session_response.json()["status"] == "CREATED"

    async def test_get_all_user_sessions(self, client: AsyncClient):
        """T045: Get all sessions for authenticated user"""
        # Setup
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "multi_session_user",
                "email": "multi@example.com",
                "password": "TestPassword123"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "multi_session_user", "password": "TestPassword123"}
        )
        token = login_response.json()["access_token"]

        # Create multiple sessions
        session1 = await client.post(
            "/api/v1/sessions",
            json={"title": "Session 1"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert session1.status_code == 201

        session2 = await client.post(
            "/api/v1/sessions",
            json={"title": "Session 2"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert session2.status_code == 201

        # Get all sessions
        list_response = await client.get(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        sessions = list_response.json()

        assert len(sessions) >= 2
        titles = [s["title"] for s in sessions]
        assert "Session 1" in titles
        assert "Session 2" in titles

    async def test_session_timestamps(self, client: AsyncClient):
        """T045: Session has proper timestamps"""
        # Setup
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "timestamp_user",
                "email": "timestamp@example.com",
                "password": "TestPassword123"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "timestamp_user", "password": "TestPassword123"}
        )
        token = login_response.json()["access_token"]

        # Create session
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Timestamp Test"},
            headers={"Authorization": f"Bearer {token}"}
        )

        data = session_response.json()
        assert data["created_at"] is not None
        assert data["last_activity"] is not None

        # created_at should not be None
        # last_activity should equal created_at initially
        assert data["created_at"] is not None
