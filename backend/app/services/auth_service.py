"""
Authentication Service Layer

Encapsulates token issuance, refresh-session tracking, rotation reuse
detection, revocation (logout), and password change. The backend is the
authority for token lifecycle management.
"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.log import get_request_id
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    is_token_revoked,
    revoke_token,
    verify_password,
)
from app.models import RefreshSession, TokenBlacklist, User
from app.services.user_service import UserService

logger = logging.getLogger("medcore.auth")


class AuthService:
    @staticmethod
    async def issue_tokens(db: AsyncSession, user: User) -> dict:
        """Create access + refresh token pair and record the refresh session."""
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role, "email": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "role": user.role}
        )

        # Record the refresh session for rotation/reuse tracking
        refresh_payload = decode_token(refresh_token)
        expires_at = datetime.fromtimestamp(
            refresh_payload["exp"], tz=timezone.utc
        ).replace(tzinfo=None)
        session = RefreshSession(
            user_id=user.id,
            jti=refresh_payload["jti"],
            expires_at=expires_at,
            revoked=False,
        )
        db.add(session)
        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": UserResponse_model(user),
        }

    @staticmethod
    async def refresh(db: AsyncSession, raw_refresh_token: str) -> dict:
        """Validate a refresh token, detect rotated-token reuse, and issue a new pair."""
        try:
            payload = decode_token(raw_refresh_token)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            ) from None

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        jti = payload.get("jti")
        user_id = payload.get("sub")
        if not jti or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Revoked refresh token check
        if await is_token_revoked(db, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        # Load the refresh session record
        session = await db.scalar(
            select(RefreshSession).where(RefreshSession.jti == jti)
        )

        if session is None:
            # Token not in our records: could be a rotated (reused) token.
            # Treat as revoked to prevent refresh-token reuse.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        user = await UserService.get_user_by_id(db, int(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        if session.revoked:
            # A rotated session should only be used once. If reused, revoke
            # all sessions for the user (token-theft signal) and reject.
            await AuthService.revoke_all_user_sessions(db, user.id)
            logger.warning(
                "refresh_token_reuse_detected",
                extra={
                    "_extra": {
                        "user_id": user.id,
                        "request_id": get_request_id(),
                    }
                },
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token reuse detected",
            )

        if session.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Saturate (single-use) the old refresh session, then issue a new pair
        session.revoked = True
        await db.commit()

        return await AuthService.issue_tokens(db, user)

    @staticmethod
    async def logout(db: AsyncSession, user: User, raw_token: str, is_access: bool = True):
        """Revoke the presented token server-side. Idempotent."""
        try:
            payload = decode_token(raw_token)
        except HTTPException:
            return  # already invalid; nothing to revoke

        jti = payload.get("jti")
        token_type = payload.get("type")
        exp = payload.get("exp")

        if not jti:
            return

        await revoke_token(
            db,
            jti=jti,
            token_type=token_type or ("access" if is_access else "refresh"),
            expires_at=datetime.fromtimestamp(exp, tz=timezone.utc)
            if exp
            else datetime.now(timezone.utc) + timedelta(minutes=5),
        )

        # Also revoke the matching refresh session if a refresh token was given
        if token_type == "refresh":
            session = await db.scalar(
                select(RefreshSession).where(RefreshSession.jti == jti)
            )
            if session and session.user_id == user.id:
                session.revoked = True
                await db.commit()

    @staticmethod
    async def revoke_all_user_sessions(db: AsyncSession, user_id: int):
        """Revoke every refresh session belonging to a user (e.g. password change)."""
        sessions = (
            await db.execute(
                select(RefreshSession).where(RefreshSession.user_id == user_id)
            )
        ).scalars().all()
        for s in sessions:
            s.revoked = True
        await db.commit()

    @staticmethod
    async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
        """Change the user's password and revoke all their refresh sessions."""
        if not verify_password(old_password, user.hashed_password):
            logger.info(
                "password_change_failed_wrong_current",
                extra={"_extra": {"user_id": user.id, "request_id": get_request_id()}},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        await db.refresh(user)

        await AuthService.revoke_all_user_sessions(db, user.id)
        logger.info(
            "password_changed",
            extra={"_extra": {"user_id": user.id, "request_id": get_request_id()}},
        )

    @staticmethod
    async def cleanup_expired_sessions(db: AsyncSession):
        """Remove expired refresh sessions (housekeeping)."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        await db.execute(
            delete(RefreshSession).where(RefreshSession.expires_at < now)
        )
        await db.execute(
            delete(TokenBlacklist).where(TokenBlacklist.expires_at < now)
        )
        await db.commit()


def UserResponse_model(user: User):
    """Serialise a user ORM instance to the UserResponse schema without circular import."""
    from app.schemas import UserResponse
    return UserResponse.model_validate(user)
