"""Интеграционные тесты: эндпоинты /auth/*."""

from datetime import timedelta

from httpx import AsyncClient

from app.services.auth import create_access_token


class TestRegister:
    async def test_success(self, client: AsyncClient):
        resp = await client.post(
            "/auth/register",
            json={"email": "new@test.com", "password": "securepass123"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@test.com"
        assert "id" in data
        assert "created_at" in data
        # Пароль не возвращается
        assert "hashed_password" not in data

    async def test_duplicate_email(self, client: AsyncClient):
        await client.post(
            "/auth/register",
            json={"email": "dup@test.com", "password": "securepass123"},
        )
        resp = await client.post(
            "/auth/register",
            json={"email": "dup@test.com", "password": "otherpass123"},
        )
        assert resp.status_code == 409

    async def test_invalid_email(self, client: AsyncClient):
        resp = await client.post(
            "/auth/register",
            json={"email": "not-email", "password": "securepass123"},
        )
        assert resp.status_code == 422

    async def test_short_password(self, client: AsyncClient):
        resp = await client.post(
            "/auth/register",
            json={"email": "user@test.com", "password": "short"},
        )
        assert resp.status_code == 422

    async def test_missing_fields(self, client: AsyncClient):
        resp = await client.post("/auth/register", json={})
        assert resp.status_code == 422


class TestLogin:
    async def test_success(self, client: AsyncClient):
        # Регистрируем пользователя
        await client.post(
            "/auth/register",
            json={"email": "login@test.com", "password": "securepass123"},
        )
        # Логинимся (OAuth2 форма — form data, не JSON)
        resp = await client.post(
            "/auth/login",
            data={"username": "login@test.com", "password": "securepass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_wrong_password(self, client: AsyncClient):
        await client.post(
            "/auth/register",
            json={"email": "login2@test.com", "password": "securepass123"},
        )
        resp = await client.post(
            "/auth/login",
            data={"username": "login2@test.com", "password": "wrongpass"},
        )
        assert resp.status_code == 401

    async def test_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            "/auth/login",
            data={"username": "ghost@test.com", "password": "anypass123"},
        )
        assert resp.status_code == 401


class TestMe:
    async def test_authenticated(self, auth_client: AsyncClient):
        resp = await auth_client.get("/auth/me")
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    async def test_no_token(self, client: AsyncClient):
        resp = await client.get("/auth/me")
        assert resp.status_code == 401

    async def test_expired_token(self, client: AsyncClient):
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
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401
