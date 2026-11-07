import asyncio
import uuid

import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import SETTINGS
from app.db import get_session
from app.users.deps import get_current_user
from app.users.models import RefreshToken, User
from app.users.schemas import LoginIn, RegisterIn, TokenOut, UserOut
from app.users.security import (
    DUMMY_HASH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE = "refresh_token"
COOKIE_PATH = "/auth"  # cookie is only sent to /auth/*; keep in sync with prefix


def _unauthorized(detail: str = "Invalid credentials") -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail)


async def _issue_tokens(session: AsyncSession, response: Response, user_id: uuid.UUID) -> str:
    jti = uuid.uuid4()
    refresh, exp = create_refresh_token(user_id, jti)
    session.add(RefreshToken(jti=jti, user_id=user_id, expires_at=exp))
    await session.commit()
    response.set_cookie(
        COOKIE,
        refresh,
        max_age=SETTINGS.refresh_ttl_days * 86400,
        httponly=True,
        secure=SETTINGS.cookie_secure,
        samesite="lax",
        path=COOKIE_PATH,
    )
    return create_access_token(user_id)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterIn, session: AsyncSession = Depends(get_session)):
    username = body.username.lower()
    exists = await session.scalar(select(User.id).where(User.username == username))
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")

    pw_hash = await asyncio.to_thread(hash_password, body.password)  # CPU-bound
    user = User(username=username, password_hash=pw_hash)
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:  # lost a race with a concurrent register
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    return user


@router.post("/login", response_model=TokenOut)
async def login(
    body: LoginIn, response: Response, session: AsyncSession = Depends(get_session)
):
    user = await session.scalar(select(User).where(User.username == body.username.lower()))
    # always run a verify so response time doesn't reveal whether the username exists
    ok = await asyncio.to_thread(
        verify_password, body.password, user.password_hash if user else DUMMY_HASH
    )
    if user is None or not ok or not user.is_active:
        raise _unauthorized()
    return TokenOut(access_token=await _issue_tokens(session, response, user.id))


@router.post("/refresh", response_model=TokenOut)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=COOKIE),
    session: AsyncSession = Depends(get_session),
):
    if refresh_token is None:
        raise _unauthorized("Missing refresh token")
    try:
        claims = decode_token(refresh_token, "refresh")
    except jwt.PyJWTError:
        raise _unauthorized("Invalid refresh token")
    jti, user_id = uuid.UUID(claims["jti"]), uuid.UUID(claims["sub"])

    # atomically claim the token: only one concurrent request can win
    claimed = await session.scalar(
        update(RefreshToken)
        .where(RefreshToken.jti == jti, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=func.now())
        .returning(RefreshToken.jti)
    )
    if claimed is None:
        # unknown or already used -> possible theft; kill every session for this user
        await session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=func.now())
        )
        await session.commit()
        # return (not raise) so the cookie deletion actually reaches the client
        rejected = JSONResponse(
            {"detail": "Refresh token reuse detected"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        rejected.delete_cookie(COOKIE, path=COOKIE_PATH)
        return rejected

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        await session.commit()
        raise _unauthorized("Invalid refresh token")
    return TokenOut(access_token=await _issue_tokens(session, response, user_id))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=COOKIE),
    session: AsyncSession = Depends(get_session),
):
    if refresh_token:
        try:
            jti = uuid.UUID(decode_token(refresh_token, "refresh")["jti"])
            await session.execute(
                update(RefreshToken)
                .where(RefreshToken.jti == jti, RefreshToken.revoked_at.is_(None))
                .values(revoked_at=func.now())
            )
            await session.commit()
        except jwt.PyJWTError:
            pass  # expired/garbage token: nothing to revoke, still clear the cookie
    response.delete_cookie(COOKIE, path=COOKIE_PATH)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user