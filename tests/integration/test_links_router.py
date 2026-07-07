"""Интеграционные тесты: эндпоинты /links/* и редирект /{code}."""

from httpx import AsyncClient

from app.services.auth import create_access_token
from app.services.link import create_link
from app.services.user import create_user


class TestCreateLink:
    async def test_success(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/links",
            json={"original_url": "https://example.com/page"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["original_url"] == "https://example.com/page"
        assert "short_url" in data
        assert len(data["short_code"]) == 7

    async def test_with_custom_alias(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/links",
            json={"original_url": "https://example.com", "custom_alias": "my-custom"},
        )
        assert resp.status_code == 201
        assert resp.json()["short_code"] == "my-custom"

    async def test_reserved_alias(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/links",
            json={"original_url": "https://example.com", "custom_alias": "docs"},
        )
        assert resp.status_code == 400
        assert "зарезервированное" in resp.json()["detail"]

    async def test_duplicate_alias(self, auth_client: AsyncClient, db_session):
        # Создаём ссылку напрямую через сервис
        user = await create_user(db_session, "dup_link@test.com", "password123")
        await create_link(db_session, "https://a.com", custom_alias="existing", user_id=user.id)

        resp = await auth_client.post(
            "/links",
            json={"original_url": "https://b.com", "custom_alias": "existing"},
        )
        assert resp.status_code == 409

    async def test_unauthorized(self, client: AsyncClient):
        resp = await client.post(
            "/links",
            json={"original_url": "https://example.com"},
        )
        assert resp.status_code == 401

    async def test_invalid_url(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/links",
            json={"original_url": "not-a-url"},
        )
        assert resp.status_code == 422


class TestGetAllLinks:
    async def test_empty(self, auth_client: AsyncClient):
        resp = await auth_client.get("/links")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {"items": [], "total": 0, "limit": 20, "offset": 0}

    async def test_returns_own_links(self, auth_client: AsyncClient):
        await auth_client.post("/links", json={"original_url": "https://a.com"})
        await auth_client.post("/links", json={"original_url": "https://b.com"})

        resp = await auth_client.get("/links")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    async def test_newest_first(self, auth_client: AsyncClient):
        await auth_client.post(
            "/links", json={"original_url": "https://a.com", "custom_alias": "first1"}
        )
        await auth_client.post(
            "/links", json={"original_url": "https://b.com", "custom_alias": "second2"}
        )

        resp = await auth_client.get("/links")
        codes = [item["short_code"] for item in resp.json()["items"]]
        assert codes == ["second2", "first1"]

    async def test_pagination(self, auth_client: AsyncClient):
        for i in range(3):
            await auth_client.post("/links", json={"original_url": f"https://a.com/{i}"})

        resp = await auth_client.get("/links", params={"limit": 1, "offset": 1})
        data = resp.json()
        assert resp.status_code == 200
        assert len(data["items"]) == 1
        assert data["total"] == 3
        assert data["limit"] == 1
        assert data["offset"] == 1

    async def test_limit_too_small(self, auth_client: AsyncClient):
        resp = await auth_client.get("/links", params={"limit": 0})
        assert resp.status_code == 422

    async def test_limit_too_large(self, auth_client: AsyncClient):
        resp = await auth_client.get("/links", params={"limit": 101})
        assert resp.status_code == 422

    async def test_not_others_links(self, client: AsyncClient, db_session):
        # Создаём ссылку от одного пользователя
        user1 = await create_user(db_session, "owner1@test.com", "password123")
        await create_link(db_session, "https://secret.com", custom_alias="prv123", user_id=user1.id)

        # Логинимся как другой пользователь
        user2 = await create_user(db_session, "viewer@test.com", "password123")
        token = create_access_token(data={"sub": user2.email})
        client.headers["Authorization"] = f"Bearer {token}"

        resp = await client.get("/links")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    async def test_unauthorized(self, client: AsyncClient):
        resp = await client.get("/links")
        assert resp.status_code == 401


class TestGetLinkInfo:
    async def test_success(self, auth_client: AsyncClient):
        await auth_client.post(
            "/links",
            json={"original_url": "https://example.com", "custom_alias": "info123"},
        )
        resp = await auth_client.get("/links/info123")
        assert resp.status_code == 200
        assert resp.json()["short_code"] == "info123"
        assert resp.json()["original_url"] == "https://example.com/"

    async def test_not_found(self, client: AsyncClient):
        resp = await client.get("/links/nonexistent")
        assert resp.status_code == 404


class TestRedirect:
    async def test_success(self, auth_client: AsyncClient, client: AsyncClient):
        await auth_client.post(
            "/links",
            json={"original_url": "https://example.com", "custom_alias": "redir1"},
        )
        # follow_redirects=False — ловим сам редирект, а не идём по нему
        resp = await client.get("/redir1", follow_redirects=False)
        assert resp.status_code == 307
        assert resp.headers["location"] == "https://example.com/"

    async def test_increments_clicks(self, auth_client: AsyncClient, client: AsyncClient):
        await auth_client.post(
            "/links",
            json={"original_url": "https://example.com", "custom_alias": "clicks1"},
        )

        await client.get("/clicks1", follow_redirects=False)
        await client.get("/clicks1", follow_redirects=False)

        info_resp = await client.get("/links/clicks1")
        assert info_resp.json()["clicks_count"] == 2

    async def test_not_found(self, client: AsyncClient):
        resp = await client.get("/nonexistent", follow_redirects=False)
        assert resp.status_code == 404
