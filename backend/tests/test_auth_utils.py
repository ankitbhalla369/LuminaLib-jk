import pytest
from app.auth import hash_password, verify_password, create_token, decode_token


def test_hash_password():
    """Test password hashing."""
    password = "testpassword"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 0


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "testpassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "testpassword"
    hashed = hash_password(password)
    assert verify_password("wrongpassword", hashed) is False


def test_create_token():
    """Test JWT token creation."""
    data = {"sub": "123"}
    token = create_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token_valid():
    """Test decoding a valid token."""
    data = {"sub": "123", "test": "value"}
    token = create_token(data)
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "123"
    assert "exp" in decoded


def test_decode_token_invalid():
    """Test decoding an invalid token."""
    invalid_token = "invalid.token.here"
    decoded = decode_token(invalid_token)
    assert decoded is None
