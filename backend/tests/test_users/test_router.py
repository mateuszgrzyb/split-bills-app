from http.cookies import SimpleCookie
import uuid
from unittest.mock import AsyncMock, Mock

import httpx2
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError

from app.db import get_session
from app.users import router
from app.users.models import RefreshToken, User
from app.users.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


@pytest_asyncio.fixture
async def api_client():
    app = FastAPI()
    app.include_router(router.router)
    session = AsyncMock()

    def add(record):
        if isinstance(record, User):
            record.id = record.id or uuid.uuid4()
            record.is_active = True if record.is_active is None else record.is_active

    session.add = Mock(side_effect=add)

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = httpx2.ASGITransport(app=app)
    async with httpx2.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, session, app


def _refresh_cookie(response) -> str:
    cookies = SimpleCookie()
    cookies.load(response.headers["set-cookie"])
    return cookies[router.COOKIE].value


def _set_refresh_cookie(client, token: str) -> None:
    client.cookies.set(router.COOKIE, token, path=router.COOKIE_PATH)


def test_auth_routes_publish_response_schemas():
    # Given an app that includes the users router
    app = FastAPI()
    app.include_router(router.router)

    # When the OpenAPI schema is generated
    paths = app.openapi()["paths"]

    # Then response models are documented for every auth route
    expected_schemas = {
        ("/auth/register", "post", "201"): "UserOut",
        ("/auth/login", "post", "200"): "TokenOut",
        ("/auth/refresh", "post", "200"): "TokenOut",
        ("/auth/me", "get", "200"): "UserOut",
    }
    for (path, method, status_code), schema_name in expected_schemas.items():
        response_schema = paths[path][method]["responses"][status_code]["content"][
            "application/json"
        ]["schema"]
        assert response_schema["$ref"].endswith(f"/{schema_name}")


@pytest.mark.asyncio
async def test_register_persists_normalized_user_with_hashed_password(api_client):
    # Given a valid registration request and an unused username
    client, session, _ = api_client
    session.scalar.return_value = None

    # When the user registers
    response = await client.post(
        "/auth/register", json={"username": "ALICE", "password": "password"}
    )

    # Then an account with a normalized username and hashed password is created
    assert response.status_code == 201
    assert response.json()["username"] == "alice"
    user = session.add.call_args.args[0]
    assert isinstance(user, User)
    assert user.password_hash != "password"
    assert verify_password("password", user.password_hash)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_rejects_existing_username(api_client):
    # Given a username that already exists
    client, session, _ = api_client
    session.scalar.return_value = uuid.uuid4()

    # When the same username is registered with different casing
    response = await client.post(
        "/auth/register", json={"username": "ALICE", "password": "password"}
    )

    # Then registration returns a conflict
    assert response.status_code == 409
    session.add.assert_not_called()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_handles_concurrent_duplicate_username(api_client):
    # Given a username that becomes taken before the insert commits
    client, session, _ = api_client
    session.scalar.return_value = None
    session.commit.side_effect = IntegrityError("insert", {}, RuntimeError("unique"))

    # When the registration loses the uniqueness race
    response = await client.post(
        "/auth/register", json={"username": "alice", "password": "password"}
    )

    # Then it returns a conflict and rolls back
    assert response.status_code == 409
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_issues_access_token_and_persists_refresh_cookie(api_client):
    # Given an active user with a valid password hash
    client, session, _ = api_client
    user = User(
        id=uuid.uuid4(),
        username="alice",
        password_hash=hash_password("password"),
        is_active=True,
    )
    session.scalar.return_value = user

    # When the user logs in
    response = await client.post(
        "/auth/login", json={"username": "ALICE", "password": "password"}
    )

    # Then access and refresh tokens are issued and the refresh token is stored
    assert response.status_code == 200
    assert decode_token(response.json()["access_token"], "access")["sub"] == str(user.id)
    refresh_record = session.add.call_args.args[0]
    assert isinstance(refresh_record, RefreshToken)
    assert refresh_record.user_id == user.id
    assert "httponly" in response.headers["set-cookie"].lower()
    assert decode_token(_refresh_cookie(response), "refresh")["jti"] == str(
        refresh_record.jti
    )
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("user", "password"),
    [
        (None, "password"),
        (User(id=uuid.uuid4(), username="alice", password_hash="", is_active=True), "wrong"),
        (
            User(
                id=uuid.uuid4(),
                username="alice",
                password_hash="",
                is_active=False,
            ),
            "password",
        ),
    ],
    ids=("unknown-user", "wrong-password", "inactive-user"),
)
async def test_login_rejects_invalid_credentials(api_client, user, password):
    # Given an unknown user, wrong password, or inactive account
    client, session, _ = api_client
    if user is not None:
        user.password_hash = hash_password("password")
    session.scalar.return_value = user

    # When login is attempted
    response = await client.post(
        "/auth/login", json={"username": "alice", "password": password}
    )

    # Then authentication fails without issuing a refresh cookie
    assert response.status_code == 401
    assert "set-cookie" not in response.headers
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_rotates_token_and_revokes_old_token(api_client):
    # Given a valid refresh token for an active user
    client, session, _ = api_client
    user = User(id=uuid.uuid4(), username="alice", password_hash="hash", is_active=True)
    old_jti = uuid.uuid4()
    old_token, _ = create_refresh_token(user.id, old_jti)
    session.scalar.return_value = old_jti
    session.get.return_value = user

    # When the refresh token is used
    _set_refresh_cookie(client, old_token)
    response = await client.post("/auth/refresh")

    # Then a new access and refresh token are issued and the old token is claimed
    assert response.status_code == 200
    assert decode_token(response.json()["access_token"], "access")["sub"] == str(user.id)
    new_token = _refresh_cookie(response)
    assert decode_token(new_token, "refresh")["jti"] != str(old_jti)
    assert "httponly" in response.headers["set-cookie"].lower()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_reuse_revokes_remaining_sessions(api_client):
    # Given a refresh token that has already been claimed
    client, session, _ = api_client
    user_id = uuid.uuid4()
    reused_token, _ = create_refresh_token(user_id, uuid.uuid4())
    session.scalar.return_value = None

    # When the token is presented again
    _set_refresh_cookie(client, reused_token)
    response = await client.post("/auth/refresh")

    # Then reuse is rejected and all of the user's remaining tokens are revoked
    assert response.status_code == 401
    assert response.json() == {"detail": "Refresh token reuse detected"}
    assert "max-age=0" in response.headers["set-cookie"].lower()
    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_rejects_missing_and_invalid_tokens(api_client):
    # Given a client without a valid refresh token
    client, _, _ = api_client

    # When refreshing without a token or with malformed token data
    missing = await client.post("/auth/refresh")
    _set_refresh_cookie(client, "not-a-token")
    malformed = await client.post("/auth/refresh")

    # Then both requests are unauthorized
    assert missing.status_code == 401
    assert malformed.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rejects_token_for_inactive_user(api_client):
    # Given an inactive user with a valid refresh token
    client, session, _ = api_client
    user = User(id=uuid.uuid4(), username="inactive", password_hash="hash", is_active=False)
    token_id = uuid.uuid4()
    token, _ = create_refresh_token(user.id, token_id)
    session.scalar.return_value = token_id
    session.get.return_value = user

    # When the inactive user's token is refreshed
    _set_refresh_cookie(client, token)
    response = await client.post("/auth/refresh")

    # Then the refresh is unauthorized
    assert response.status_code == 401
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token_and_clears_cookie(api_client):
    # Given a valid refresh token
    client, session, _ = api_client
    token, _ = create_refresh_token(uuid.uuid4(), uuid.uuid4())

    # When the user logs out
    _set_refresh_cookie(client, token)
    response = await client.post("/auth/logout")

    # Then the token is revoked and its cookie is deleted
    assert response.status_code == 204
    assert "max-age=0" in response.headers["set-cookie"].lower()
    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("token", [None, "malformed"], ids=("missing", "malformed"))
async def test_logout_clears_cookie_without_valid_refresh_token(api_client, token):
    # Given no refresh token or malformed refresh-token data
    client, session, _ = api_client
    if token is not None:
        _set_refresh_cookie(client, token)

    # When the user logs out
    response = await client.post("/auth/logout")

    # Then the cookie is deleted without a database update
    assert response.status_code == 204
    assert "max-age=0" in response.headers["set-cookie"].lower()
    session.execute.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_me_returns_the_authenticated_user(api_client):
    # Given an active user and valid bearer credentials
    client, session, _ = api_client
    user = User(id=uuid.uuid4(), username="alice", password_hash="hash", is_active=True)
    session.get.return_value = user

    # When the user requests their profile
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {create_access_token(user.id)}"},
    )

    # Then the authenticated user's public profile is returned
    assert response.status_code == 200
    assert response.json() == {"id": str(user.id), "username": "alice"}