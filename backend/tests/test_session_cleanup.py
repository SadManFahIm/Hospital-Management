"""
Session / token housekeeping tests.

Verifies that AuthService.cleanup_expired_sessions removes only records that
have fully expired, and preserves revoked-but-unexpired refresh sessions
(required for refresh-token reuse detection) and unexpired blacklist entries.
"""

import asyncio
from datetime import datetime, timedelta

from app.core.database import AsyncSessionLocal
from app.models import RefreshSession, TokenBlacklist
from app.services.auth_service import AuthService
from sqlalchemy import select


def _now_naive():
    return datetime.utcnow()


def _run(coro):
    return asyncio.run(coro)


def test_cleanup_removes_expired_records_only(admin_user):
    now = _now_naive()
    admin_id = admin_user

    async def _seed():
        async with AsyncSessionLocal() as db:
            db.add_all(
                [
                    # expired refresh session -> removed
                    RefreshSession(
                        user_id=admin_id,
                        jti="expired-ref",
                        expires_at=now - timedelta(days=1),
                        revoked=False,
                    ),
                    # revoked but still valid -> KEPT (reuse-detection signal)
                    RefreshSession(
                        user_id=admin_id,
                        jti="revoked-active",
                        expires_at=now + timedelta(days=1),
                        revoked=True,
                    ),
                    # valid, unused -> KEPT
                    RefreshSession(
                        user_id=admin_id,
                        jti="active-ref",
                        expires_at=now + timedelta(days=1),
                        revoked=False,
                    ),
                    # expired blacklist entry -> removed
                    TokenBlacklist(
                        jti="expired-bl",
                        token_type="access",
                        expires_at=now - timedelta(minutes=1),
                    ),
                    # valid blacklist entry -> KEPT
                    TokenBlacklist(
                        jti="active-bl",
                        token_type="access",
                        expires_at=now + timedelta(minutes=5),
                    ),
                ]
            )
            await db.commit()

    async def _cleanup():
        async with AsyncSessionLocal() as db:
            await AuthService.cleanup_expired_sessions(db)

    async def _snapshot():
        async with AsyncSessionLocal() as db:
            refs = {
                (r.jti, r.revoked)
                for r in (await db.execute(select(RefreshSession))).scalars()
            }
            bls = {b.jti for b in (await db.execute(select(TokenBlacklist))).scalars()}
            return refs, bls

    _run(_seed())
    _run(_cleanup())
    refs, bls = _run(_snapshot())

    # Expired refresh session removed
    assert all(jti != "expired-ref" for jti, _ in refs)
    # Revoked-but-valid session preserved (reuse detection)
    assert ("revoked-active", True) in refs
    # Valid session preserved
    assert ("active-ref", False) in refs
    # Expired blacklist entry removed, valid one preserved
    assert "expired-bl" not in bls
    assert "active-bl" in bls
