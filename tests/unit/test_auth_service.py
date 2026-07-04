"""Тесты сервиса авторизации: хэширование паролей и JWT."""

from datetime import timedelta

import jwt
import pytest

from app.services.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_returns_bcrypt_string(self):
        result = hash_password("mypassword")
        assert result.startswith("$2b$")

    def test_unique_salt(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_verify_correct(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_verify_wrong(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False


class TestJWT:
    def test_create_contains_sub_and_exp(self):
        token = create_access_token(data={"sub": "user@test.com"})
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["sub"] == "user@test.com"
        assert "exp" in payload

    def test_create_custom_expiry(self):
        token = create_access_token(
            data={"sub": "user@test.com"},
            expires_delta=timedelta(hours=2),
        )
        payload = jwt.decode(token, options={"verify_signature": False})
        assert "exp" in payload

    def test_decode_valid(self):
        token = create_access_token(data={"sub": "user@test.com"})
        payload = decode_access_token(token)
        assert payload["sub"] == "user@test.com"

    def test_decode_expired(self):
        token = create_access_token(
            data={"sub": "user@test.com"},
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(token)

    def test_decode_invalid_signature(self):
        token = jwt.encode({"sub": "hacker"}, "wrong-secret", algorithm="HS256")
        with pytest.raises(jwt.InvalidSignatureError):
            decode_access_token(token)

    def test_decode_malformed(self):
        with pytest.raises(jwt.DecodeError):
            decode_access_token("not.a.jwt")
