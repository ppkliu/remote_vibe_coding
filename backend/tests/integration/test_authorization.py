"""
Integration tests for session authorization (T119)

Tests that verify session ownership validation:
- Users can only access their own sessions
- Users cannot access other users' sessions
- Session CRUD operations enforce ownership
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from src.models.user import User
from src.models.session import Session


@pytest.fixture
async def user_and_token(client: AsyncClient, db: AsyncSession):
    """Create test user and return auth token"""
    # Register user
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": f"user_{uuid.uuid4().hex[:8]}",
            "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123"
        }
    )

    # Login
    username = response.json()["username"]
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": "TestPassword123"
        }
    )

    token = login_response.json()["access_token"]

    # Get user object
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalar_one()

    return user, token


@pytest.fixture
async def user1_and_token(client: AsyncClient, db: AsyncSession):
    """Create first test user with token"""
    return await user_and_token(client, db)


@pytest.fixture
async def user2_and_token(client: AsyncClient, db: AsyncSession):
    """Create second test user with token"""
    return await user_and_token(client, db)


class TestSessionAuthorization:
    """Test session ownership validation (T123, T119)"""

    async def test_user_can_create_session(self, client: AsyncClient, user1_and_token):
        """T119: User can create a session"""
        user, token = user1_and_token
        response = await client.post(
            "/api/v1/sessions",
            json={"title": "Test Session"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Session"
        assert data["user_id"] == str(user.id)

    async def test_user_can_view_own_sessions(self, client: AsyncClient, user1_and_token):
        """T123: User can view their own sessions"""
        user, token = user1_and_token

        # Create session
        await client.post(
            "/api/v1/sessions",
            json={"title": "My Session"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # List sessions
        response = await client.get(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        sessions = response.json()
        assert len(sessions) >= 1
        assert sessions[0]["title"] == "My Session"

    async def test_user_cannot_view_other_sessions(
        self, client: AsyncClient, user1_and_token, user2_and_token
    ):
        """T123: User cannot view other users' sessions"""
        user1, token1 = user1_and_token
        user2, token2 = user2_and_token

        # User1 creates session
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "User1 Private Session"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        session_id = session_response.json()["id"]

        # User2 tries to access User1's session
        response = await client.get(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_user_cannot_modify_other_sessions(
        self, client: AsyncClient, user1_and_token, user2_and_token
    ):
        """T123: User cannot modify other users' sessions"""
        user1, token1 = user1_and_token
        user2, token2 = user2_and_token

        # User1 creates session
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Original Title"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        session_id = session_response.json()["id"]

        # User2 tries to update User1's session
        response = await client.patch(
            f"/api/v1/sessions/{session_id}",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 404

    async def test_user_cannot_delete_other_sessions(
        self, client: AsyncClient, user1_and_token, user2_and_token
    ):
        """T123: User cannot delete other users' sessions"""
        user1, token1 = user1_and_token
        user2, token2 = user2_and_token

        # User1 creates session
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Session to Protect"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        session_id = session_response.json()["id"]

        # User2 tries to delete User1's session
        response = await client.delete(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 404

        # Verify session still exists for User1
        response = await client.get(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token1}"}
        )
        assert response.status_code == 200

    async def test_user_cannot_access_other_session_messages(
        self, client: AsyncClient, user1_and_token, user2_and_token
    ):
        """T123: User cannot access other users' session messages"""
        user1, token1 = user1_and_token
        user2, token2 = user2_and_token

        # User1 creates session
        session_response = await client.post(
            "/api/v1/sessions",
            json={"title": "Private Session"},
            headers={"Authorization": f"Bearer {token1}"}
        )
        session_id = session_response.json()["id"]

        # User2 tries to get User1's messages
        response = await client.get(
            f"/api/v1/sessions/{session_id}/messages",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert response.status_code == 404

    async def test_unauthenticated_cannot_create_session(self, client: AsyncClient):
        """T119: Unauthenticated user cannot create session"""
        response = await client.post(
            "/api/v1/sessions",
            json={"title": "Unauthorized Session"}
        )
        assert response.status_code == 401

    async def test_unauthenticated_cannot_list_sessions(self, client: AsyncClient):
        """T119: Unauthenticated user cannot list sessions"""
        response = await client.get("/api/v1/sessions")
        assert response.status_code == 401

    async def test_invalid_token_cannot_access_sessions(self, client: AsyncClient):
        """T119: Invalid token cannot access sessions"""
        response = await client.get(
            "/api/v1/sessions",
            headers={"Authorization": "Bearer invalid.token.xyz"}
        )
        assert response.status_code == 401


class TestRateLimiting:
    """Test rate limiting headers (T121-T122)"""

    async def test_rate_limit_headers_present(self, client: AsyncClient, user1_and_token):
        """T122: Rate limit headers in response"""
        user, token = user1_and_token
        response = await client.post(
            "/api/v1/sessions",
            json={"title": "Test"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "10"

    async def test_rate_limit_enforcement(self, client: AsyncClient, user1_and_token):
        """T121: Rate limiting enforces 10 commands per minute"""
        user, token = user1_and_token

        # Make 11 requests (exceeds limit of 10)
        responses = []
        for i in range(11):
            response = await client.post(
                "/api/v1/sessions",
                json={"title": f"Session {i}"},
                headers={"Authorization": f"Bearer {token}"}
            )
            responses.append(response)

        # First 10 should succeed
        for i in range(10):
            assert responses[i].status_code == 201

        # 11th should be rate limited
        assert responses[10].status_code == 429
        assert "Rate limit exceeded" in responses[10].json()["detail"]
