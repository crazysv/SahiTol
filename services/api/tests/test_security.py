"""Tests for security: Argon2id PIN hashing and JWT issuance/verification."""
from app.security import (
    hash_pin,
    verify_pin,
    create_access_token,
    create_refresh_token,
    decode_token,
    UserRole
)


def test_pin_hashing_and_verification():
    pin = "1234"
    hashed = hash_pin(pin)
    assert hashed != pin
    assert verify_pin(pin, hashed) is True
    assert verify_pin("9999", hashed) is False
    assert verify_pin("12345", hashed) is False


def test_access_token_creation_and_decoding():
    subject = "collector_user_01"
    role = UserRole.COLLECTOR
    token = create_access_token(subject=subject, role=role)
    assert isinstance(token, str)

    decoded = decode_token(token)
    assert decoded["sub"] == subject
    assert decoded["role"] == "COLLECTOR"
    assert decoded["token_type"] == "access"
    assert "exp" in decoded


def test_refresh_token():
    subject = "recycler_user_01"
    role = UserRole.RECYCLER
    token = create_refresh_token(subject=subject, role=role)
    decoded = decode_token(token)
    assert decoded["sub"] == subject
    assert decoded["role"] == "RECYCLER"
    assert decoded["token_type"] == "refresh"
