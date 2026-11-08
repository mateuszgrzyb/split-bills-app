import uuid

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.users.deps import get_current_user
from app.users.models import User
from app.users.security import create_access_token


@pytest.mark.asyncio
async def test_current_user_returns_active_user(session):
    # Given an active user persisted in PostgreSQL and valid bearer credentials
    user = User(username="alice", password_hash="hash", is_active=True)
    session.add(user)
    await session.commit()
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=create_access_token(user.id)
    )

    # When resolving the current user
    result = await get_current_user(credentials, session)

    # Then the persisted user is returned
    assert result.id == user.id
    assert result.username == "alice"


@pytest.mark.asyncio
async def test_current_user_rejects_missing_credentials(session):
    # Given a request without bearer credentials

    # When resolving the current user
    with pytest.raises(HTTPException) as raised:
        await get_current_user(None, session)

    # Then it is rejected with a bearer challenge
    assert raised.value.status_code == 401
    assert raised.value.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_current_user_rejects_inactive_user(session):
    # Given an inactive user with a valid access token
    user = User(username="inactive", password_hash="hash", is_active=False)
    session.add(user)
    await session.commit()
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=create_access_token(user.id)
    )

    # When resolving the current user
    with pytest.raises(HTTPException) as raised:
        await get_current_user(credentials, session)

    # Then authentication is rejected
    assert raised.value.status_code == 401


@pytest.mark.asyncio
async def test_current_user_rejects_token_for_unknown_user(session):
    # Given valid credentials for a user absent from PostgreSQL
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=create_access_token(uuid.uuid4())
    )

    # When resolving the current user
    with pytest.raises(HTTPException) as raised:
        await get_current_user(credentials, session)

    # Then authentication is rejected
    assert raised.value.status_code == 401


@pytest.mark.asyncio
async def test_current_user_rejects_malformed_token(session):
    # Given malformed bearer credentials
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="malformed")

    # When resolving the current user
    with pytest.raises(HTTPException) as raised:
        await get_current_user(credentials, session)

    # Then authentication is rejected
    assert raised.value.status_code == 401
