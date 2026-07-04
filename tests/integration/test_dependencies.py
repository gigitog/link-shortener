"""Интеграционные тесты: get_current_user dependency."""

from datetime import timedelta

from httpx import AsyncClient

from app.services.auth import create_access_token


class TestGetCurrentUser:
    async def test_valid_token(self, auth_client: AsyncClient):
        """Валидный токен → доступ к защищённому эндпоинту."""
        resp = await auth_client.get("/auth/me")
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    async def test_expired_token(self, client: AsyncClient):
        """Просроченный токен → 401."""
        token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(seconds=-1),
        )
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401

    async def test_invalid_token(self, client: AsyncClient):
        """Невалидный токен → 401."""
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer garbage"},
        )
        assert resp.status_code == 401

    async def test_no_sub_in_payload(self, client: AsyncClient):
        """Токен без поля 'sub' → 401."""
        token = create_access_token(data={"not_sub": "value"})
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401

    async def test_user_deleted(self, client: AsyncClient):
        """Email из токена не найден в БД → 401."""
        token = create_access_token(data={"sub": "deleted@test.com"})
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401
