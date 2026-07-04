"""Тесты сервиса пользователей: регистрация, поиск, аутентификация."""

import pytest

from app.services.user import authenticate_user, create_user, get_user_by_email


class TestCreateUser:
    async def test_success(self, db_session):
        user = await create_user(db_session, "new@test.com", "password123")
        assert user.id is not None
        assert user.email == "new@test.com"
        # Пароль хранится как хэш, а не как plain text
        assert user.hashed_password != "password123"
        assert user.hashed_password.startswith("$2b$")

    async def test_duplicate_email(self, db_session):
        await create_user(db_session, "dup@test.com", "password123")
        with pytest.raises(ValueError, match="уже существует"):
            await create_user(db_session, "dup@test.com", "other_pass")


class TestGetUserByEmail:
    async def test_found(self, db_session):
        await create_user(db_session, "find@test.com", "password123")
        user = await get_user_by_email(db_session, "find@test.com")
        assert user is not None
        assert user.email == "find@test.com"

    async def test_not_found(self, db_session):
        user = await get_user_by_email(db_session, "ghost@test.com")
        assert user is None


class TestAuthenticateUser:
    async def test_correct_credentials(self, db_session):
        await create_user(db_session, "auth@test.com", "correct_pass")
        user = await authenticate_user(db_session, "auth@test.com", "correct_pass")
        assert user is not None
        assert user.email == "auth@test.com"

    async def test_wrong_password(self, db_session):
        await create_user(db_session, "auth2@test.com", "correct_pass")
        user = await authenticate_user(db_session, "auth2@test.com", "wrong_pass")
        assert user is None

    async def test_nonexistent_email(self, db_session):
        user = await authenticate_user(db_session, "nobody@test.com", "any_pass")
        assert user is None
