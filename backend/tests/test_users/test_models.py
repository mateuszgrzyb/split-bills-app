from datetime import datetime, timezone
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.users.models import RefreshToken, User


@pytest.mark.asyncio
async def test_user_defaults_and_refresh_token_persist(session):
    # Given a new user and refresh token
    user = User(username="alice", password_hash="hashed")
    session.add(user)
    await session.flush()
    refresh_token = RefreshToken(
        jti=uuid.uuid4(),
        user_id=user.id,
        expires_at=datetime.now(timezone.utc),
    )
    session.add(refresh_token)

    # When both models are committed and reloaded
    await session.commit()
    loaded_user = await session.get(User, user.id)
    loaded_token = await session.scalar(
        select(RefreshToken).where(RefreshToken.jti == refresh_token.jti)
    )

    # Then SQLAlchemy and PostgreSQL defaults and foreign keys are applied
    assert loaded_user is not None
    assert loaded_user.is_active is True
    assert loaded_user.created_at is not None
    assert loaded_token is not None
    assert loaded_token.user_id == user.id
    assert loaded_token.revoked_at is None


@pytest.mark.asyncio
async def test_user_username_is_unique(session):
    # Given a user with an existing username
    session.add(User(username="alice", password_hash="first"))
    await session.commit()

    # When another user is inserted with the same username
    session.add(User(username="alice", password_hash="second"))

    # Then PostgreSQL enforces the unique constraint
    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.asyncio
async def test_deleting_user_cascades_to_refresh_tokens(session):
    # Given a user with a persisted refresh token
    user = User(username="alice", password_hash="hash")
    session.add(user)
    await session.flush()
    token = RefreshToken(
        jti=uuid.uuid4(), user_id=user.id, expires_at=datetime.now(timezone.utc)
    )
    session.add(token)
    await session.commit()

    # When the user is deleted
    await session.delete(user)
    await session.commit()

    # Then PostgreSQL cascades the delete to the refresh token
    persisted_token = await session.scalar(
        select(RefreshToken).where(RefreshToken.jti == token.jti)
    )
    assert persisted_token is None