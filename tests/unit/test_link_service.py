"""Тесты сервиса ссылок: создание, поиск, счётчик кликов."""

import pytest

from app.services.link import (
    create_link,
    get_all_links,
    get_link_by_code,
    increment_clicks,
)
from app.services.user import create_user


class TestCreateLink:
    async def test_random_code(self, db_session):
        user = await create_user(db_session, "link1@test.com", "password123")
        link = await create_link(db_session, "https://example.com", user_id=user.id)
        assert len(link.short_code) == 7
        assert link.original_url == "https://example.com"
        assert link.user_id == user.id

    async def test_custom_alias(self, db_session):
        user = await create_user(db_session, "link2@test.com", "password123")
        link = await create_link(
            db_session, "https://example.com", custom_alias="my-alias", user_id=user.id
        )
        assert link.short_code == "my-alias"

    async def test_duplicate_alias_raises(self, db_session):
        user = await create_user(db_session, "link3@test.com", "password123")
        await create_link(db_session, "https://a.com", custom_alias="taken", user_id=user.id)
        with pytest.raises(ValueError, match="уже занят"):
            await create_link(db_session, "https://b.com", custom_alias="taken", user_id=user.id)


class TestGetLinkByCode:
    async def test_found(self, db_session):
        user = await create_user(db_session, "get1@test.com", "password123")
        created = await create_link(
            db_session, "https://example.com", custom_alias="findme", user_id=user.id
        )
        found = await get_link_by_code(db_session, "findme")
        assert found is not None
        assert found.id == created.id

    async def test_not_found(self, db_session):
        found = await get_link_by_code(db_session, "nonexistent")
        assert found is None


class TestGetAllLinks:
    async def test_returns_user_links(self, db_session):
        user = await create_user(db_session, "all1@test.com", "password123")
        await create_link(db_session, "https://a.com", custom_alias="aaa111", user_id=user.id)
        await create_link(db_session, "https://b.com", custom_alias="bbb222", user_id=user.id)

        links = await get_all_links(db_session, user_id=user.id)
        assert len(links) == 2

    async def test_empty(self, db_session):
        user = await create_user(db_session, "all2@test.com", "password123")
        links = await get_all_links(db_session, user_id=user.id)
        assert links == []

    async def test_does_not_return_other_users_links(self, db_session):
        user1 = await create_user(db_session, "owner@test.com", "password123")
        user2 = await create_user(db_session, "other@test.com", "password123")
        await create_link(db_session, "https://a.com", custom_alias="own111", user_id=user1.id)

        links = await get_all_links(db_session, user_id=user2.id)
        assert links == []


class TestIncrementClicks:
    async def test_increments(self, db_session):
        user = await create_user(db_session, "click1@test.com", "password123")
        link = await create_link(
            db_session, "https://example.com", custom_alias="click1", user_id=user.id
        )
        assert link.clicks_count == 0

        await increment_clicks(db_session, link.id)

        updated = await get_link_by_code(db_session, "click1")
        assert updated.clicks_count == 1

    async def test_multiple_increments(self, db_session):
        user = await create_user(db_session, "click2@test.com", "password123")
        link = await create_link(
            db_session, "https://example.com", custom_alias="click2", user_id=user.id
        )

        for _ in range(3):
            await increment_clicks(db_session, link.id)

        updated = await get_link_by_code(db_session, "click2")
        assert updated.clicks_count == 3
