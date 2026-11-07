import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import SETTINGS


_hasher = PasswordHash.recommended()  # argon2id
DUMMY_HASH = _hasher.hash("not-a-real-password")  # equalizes timing for unknown usernames


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _hasher.verify(password, hashed)


def _encode(sub: str, typ: str, ttl: timedelta, jti: uuid.UUID | None = None):
    now = datetime.now(timezone.utc)
    exp = now + ttl
    claims = {"sub": sub, "typ": typ, "iat": now, "exp": exp}
    if jti:
        claims["jti"] = str(jti)
    token = jwt.encode(claims, SETTINGS.jwt_secret, algorithm=SETTINGS.jwt_algorithm)
    return token, exp


def create_access_token(user_id: uuid.UUID) -> str:
    token, _ = _encode(str(user_id), "access", timedelta(minutes=SETTINGS.access_ttl_min))
    return token


def create_refresh_token(user_id: uuid.UUID, jti: uuid.UUID) -> tuple[str, datetime]:
    return _encode(str(user_id), "refresh", timedelta(days=SETTINGS.refresh_ttl_days), jti)


def decode_token(token: str, expected_typ: str) -> dict:
    """Raises jwt.PyJWTError on any problem."""
    claims = jwt.decode(
        token,
        SETTINGS.jwt_secret,
        algorithms=[SETTINGS.jwt_algorithm],
        options={"require": ["exp", "sub", "typ"]},
    )
    if claims["typ"] != expected_typ:
        raise jwt.InvalidTokenError("wrong token type")
    return claims