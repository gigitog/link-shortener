"""Тесты Pydantic-схем: валидация входных данных."""

import pytest
from pydantic import ValidationError

from app.schemas.link import LinkCreate
from app.schemas.user import UserCreate

# --- LinkCreate ---


class TestLinkCreate:
    def test_valid_url(self):
        link = LinkCreate(original_url="https://example.com/page")
        assert str(link.original_url) == "https://example.com/page"

    def test_invalid_url(self):
        with pytest.raises(ValidationError):
            LinkCreate(original_url="not-a-url")

    def test_alias_valid(self):
        link = LinkCreate(original_url="https://example.com", custom_alias="my-link_1")
        assert link.custom_alias == "my-link_1"

    def test_alias_none_is_ok(self):
        link = LinkCreate(original_url="https://example.com")
        assert link.custom_alias is None

    def test_alias_too_short(self):
        with pytest.raises(ValidationError, match="от 3 до 30"):
            LinkCreate(original_url="https://example.com", custom_alias="ab")

    def test_alias_too_long(self):
        with pytest.raises(ValidationError, match="от 3 до 30"):
            LinkCreate(original_url="https://example.com", custom_alias="a" * 31)

    def test_alias_invalid_chars(self):
        with pytest.raises(ValidationError, match="буквы, цифры, дефис"):
            LinkCreate(original_url="https://example.com", custom_alias="my link!")


# --- UserCreate ---


class TestUserCreate:
    def test_valid(self):
        user = UserCreate(email="user@example.com", password="securepass")
        assert user.email == "user@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(email="not-email", password="securepass")

    def test_short_password(self):
        with pytest.raises(ValidationError, match="не менее 8"):
            UserCreate(email="user@example.com", password="short")

    def test_password_exactly_8_chars(self):
        user = UserCreate(email="user@example.com", password="12345678")
        assert user.password == "12345678"
