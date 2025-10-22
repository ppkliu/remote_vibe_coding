"""
Quick check tests for rapid feedback during development
"""

import pytest
from httpx import AsyncClient


class TestQuickCheck:
    """Rapid validation of core features"""

    async def test_health_check(self, client: AsyncClient):
        """Verify backend is running"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "healthy"]  # Accept either response

    async def test_register_user_simple(self, client: AsyncClient):
        """Simple user registration test"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "quicktest",
                "email": "quick@test.com",
                "password": "TestPass123"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        # Accept both 201 (created) and 400 (already exists)
        assert response.status_code in [201, 400]
