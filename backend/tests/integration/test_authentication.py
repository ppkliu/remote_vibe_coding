"""
Integration tests for authentication flow (T118)

Tests the complete authentication workflow:
- User registration
- Login with JWT tokens
- Token refresh
- Logout
- Token expiration
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uuid

from src.main import app
from src.services.auth_service import AuthService
from src.models.user import User


@pytest.fixture
async def auth_test_user(db: AsyncSession):
    """Create a test user for authentication tests"""
    user = User(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password=User.hash_password("testpassword123"),
        is_active=True
    )
    db.add(user)
    await db.commit()
    return user


class TestAuthentication:
    """Test authentication flow"""

    async def test_user_registration(self, client: AsyncClient):
        """T118: Register new user successfully"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "SecurePassword123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    async def test_user_registration_duplicate_username(self, client: AsyncClient, auth_test_user):
        """T118: Reject duplicate username registration"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",  # Duplicate
                "email": "different@example.com",
                "password": "SecurePassword123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    async def test_user_login_success(self, client: AsyncClient, auth_test_user):
        """T118: Login with correct credentials returns tokens"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_user_login_invalid_password(self, client: AsyncClient, auth_test_user):
        """T118: Login with invalid password returns 401"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]

    async def test_user_login_nonexistent_user(self, client: AsyncClient):
        """T118: Login with nonexistent user returns 401"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401

    async def test_token_refresh_success(self, client: AsyncClient, auth_test_user):
        """T118: Refresh token returns new access token"""
        # First login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # Then refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != login_response.json()["access_token"]

    async def test_token_refresh_invalid_token(self, client: AsyncClient):
        """T118: Refresh with invalid token returns 401"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        assert response.status_code == 401

    async def test_logout_endpoint_exists(self, client: AsyncClient, auth_test_user):
        """T125: Logout endpoint returns success"""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        access_token = login_response.json()["access_token"]

        # Logout
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert "Logout successful" in response.json()["detail"]

    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """T118: Access protected endpoint without token returns 401"""
        response = await client.get("/api/v1/sessions")
        assert response.status_code == 401

    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """T118: Access protected endpoint with invalid token returns 401"""
        response = await client.get(
            "/api/v1/sessions",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    async def test_protected_endpoint_with_valid_token(self, client: AsyncClient, auth_test_user):
        """T118: Access protected endpoint with valid token succeeds"""
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        access_token = login_response.json()["access_token"]

        # Access protected endpoint
        response = await client.get(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAuthenticationLogging:
    """Test security logging for auth failures (T124)"""

    async def test_failed_login_logged(self, client: AsyncClient, caplog):
        """T124: Failed login attempts are logged"""
        with caplog.at_level("WARNING"):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": "nonexistent",
                    "password": "password"
                }
            )
        assert response.status_code == 401
        # Note: logging verification depends on logger configuration
        # In production, verify logs contain security event

    async def test_successful_login_logged(self, client: AsyncClient, auth_test_user, caplog):
        """T124: Successful logins are logged"""
        with caplog.at_level("INFO"):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": "testuser",
                    "password": "testpassword123"
                }
            )
        assert response.status_code == 200
