"""
Contract tests for POST /api/v1/sessions endpoint (T044)

Validates the API contract for session creation:
- Request schema validation
- Response schema validation
- Required fields presence
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestSessionsAPIContract:
    """Test POST /api/v1/sessions API contract (T044)"""

    async def test_create_session_request_schema(self, client: AsyncClient):
        """T044: POST /api/v1/sessions accepts valid request"""
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "sessiontest",
                "email": "sessiontest@example.com",
                "password": "TestPassword123"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "sessiontest", "password": "TestPassword123"}
        )
        token = login_response.json()["access_token"]

        # Create session with valid request
        response = await client.post(
            "/api/v1/sessions",
            json={"title": "My Session"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()

        # Validate response schema
        assert "id" in data
        assert "user_id" in data
        assert "title" in data
        assert "status" in data
        assert "created_at" in data
        assert "last_activity" in data

    async def test_create_session_response_types(self, client: AsyncClient):
        """T044: POST /api/v1/sessions response has correct types"""
        # Setup
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "typetest",
                "email": "typetest@example.com",
                "password": "TestPassword123"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "typetest", "password": "TestPassword123"}
        )
        token = login_response.json()["access_token"]

        response = await client.post(
            "/api/v1/sessions",
            json={"title": "Type Test"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()

        # Type validation
        assert isinstance(data["id"], str)  # UUID as string
        assert isinstance(data["user_id"], str)  # UUID as string
        assert isinstance(data["title"], str)
        assert isinstance(data["status"], str)
        assert data["status"] in ["CREATED", "CONNECTING", "ACTIVE", "DISCONNECTED"]
        assert isinstance(data["created_at"], str)  # ISO format datetime
        assert isinstance(data["last_activity"], str)  # ISO format datetime

    async def test_create_session_minimal_request(self, client: AsyncClient):
        """T044: POST /api/v1/sessions works with minimal request"""
        # Setup
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "mintest",
                "email": "mintest@example.com",
                "password": "TestPassword123"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "mintest", "password": "TestPassword123"}
        )
        token = login_response.json()["access_token"]

        # Minimal request (empty object)
        response = await client.post(
            "/api/v1/sessions",
            json={},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should succeed with defaults
        assert response.status_code == 201
        data = response.json()
        assert data["title"] is None or data["title"] == ""

    async def test_create_session_requires_authentication(self, client: AsyncClient):
        """T044: POST /api/v1/sessions requires authentication"""
        response = await client.post(
            "/api/v1/sessions",
            json={"title": "Unauthorized"}
        )

        assert response.status_code == 401
        assert "authorization" in response.json()["detail"].lower() or \
               "unauthorized" in response.json()["detail"].lower()

    async def test_session_status_enum_values(self, client: AsyncClient):
        """T044: Session status is valid enum value"""
        # Setup
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "enumtest",
                "email": "enumtest@example.com",
                "password": "TestPassword123"
            }
        )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={"username": "enumtest", "password": "TestPassword123"}
        )
        token = login_response.json()["access_token"]

        response = await client.post(
            "/api/v1/sessions",
            json={"title": "Enum Test"},
            headers={"Authorization": f"Bearer {token}"}
        )

        data = response.json()
        valid_statuses = ["CREATED", "CONNECTING", "ACTIVE", "DISCONNECTED", "IDLE", "ENDED"]
        assert data["status"] in valid_statuses
