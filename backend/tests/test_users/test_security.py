import uuid

import jwt
import pytest

from app.users.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_verifies_only_matching_password():
    # Given a hash of the correct password
    hashed = hash_password("correct horse battery staple")

    # When checking the original and a different password
    original_matches = verify_password("correct horse battery staple", hashed)
    different_matches = verify_password("incorrect", hashed)

    # Then only the original password is accepted
    assert original_matches is True
    assert different_matches is False


def test_access_token_has_access_type_and_rejects_refresh_type():
    # Given an access token for a user
    user_id = uuid.uuid4()
    token = create_access_token(user_id)

    # When decoding it as an access token
    claims = decode_token(token, "access")

    # Then it identifies the user and rejects the wrong token type
    assert claims["sub"] == str(user_id)
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(token, "refresh")


def test_refresh_token_contains_token_id_and_expiry():
    # Given a user and refresh-token identifier
    user_id = uuid.uuid4()
    token_id = uuid.uuid4()
    token, expires_at = create_refresh_token(user_id, token_id)

    # When decoding the refresh token
    claims = decode_token(token, "refresh")

    # Then its claims identify the user and token and its expiry is in the future
    assert claims["sub"] == str(user_id)
    assert claims["jti"] == str(token_id)
    assert expires_at.timestamp() > claims["iat"]