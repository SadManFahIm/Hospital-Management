"""
Authentication Security Tests

Covers the full auth flow: login, refresh (with rotation reuse detection),
logout (server-side revocation), password change, and token revocation.
"""

import pytest
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models import User
from sqlalchemy import select


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _login(client, email, password):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def _login_tokens(client, email, password):
    data = _login(client, email, password).json()
    return data["access_token"], data["refresh_token"]


def _set_password(email, password):
    async def _do():
        async with AsyncSessionLocal() as db:
            user = await db.scalar(select(User).where(User.email == email))
            user.hashed_password = get_password_hash(password)
            await db.commit()
    import asyncio
    asyncio.run(_do())


@pytest.fixture()
def patient_ready(client, patient_user):
    """Ensure the shared patient has a known password before each test."""
    _set_password("t_patient@test.com", "Patient@1234")
    yield


# ─── Login (positive) ──────────────────────────────────────────────────────────

def test_login_success(client, admin_user):
    data = _login(client, "t_admin@test.com", "Admin@1234").json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["user"]["email"] == "t_admin@test.com"


def test_login_bad_credentials(client, admin_user):
    resp = _login(client, "t_admin@test.com", "WrongPass@123")
    assert resp.status_code == 401


# ─── Refresh (positive) ────────────────────────────────────────────────────────

def test_refresh_success_rotates(client, admin_user):
    _, refresh = _login_tokens(client, "t_admin@test.com", "Admin@1234")
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"]
    assert data["refresh_token"]
    me = client.get("/api/v1/auth/me", headers=_auth(data["access_token"]))
    assert me.status_code == 200


# ─── Refresh (negative: reuse / invalid) ──────────────────────────────────────

def test_refresh_reuse_rejected(client, admin_user):
    _, refresh = _login_tokens(client, "t_admin@test.com", "Admin@1234")
    first = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert first.status_code == 200
    # Reusing the already-rotated (single-use) refresh token must be rejected, and
    # must also revoke the user's other sessions (token-theft signal).
    second = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert second.status_code == 401


def test_refresh_invalid_token(client, admin_user):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-valid-jwt"})
    assert resp.status_code == 401


def test_refresh_missing_token(client, admin_user):
    resp = client.post("/api/v1/auth/refresh", json={})
    assert resp.status_code == 422


def test_refresh_access_token_used_as_refresh(client, admin_user):
    access, _ = _login_tokens(client, "t_admin@test.com", "Admin@1234")
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": access})
    assert resp.status_code == 401


# ─── Protected endpoints (negative) ───────────────────────────────────────────

def test_me_requires_auth(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


# ─── Logout (positive + idempotent) ───────────────────────────────────────────

def test_logout_revokes_tokens(client, admin_user):
    access, refresh = _login_tokens(client, "t_admin@test.com", "Admin@1234")

    resp = client.post(
        "/api/v1/auth/logout", headers=_auth(access), json={"refresh_token": refresh}
    )
    assert resp.status_code == 200

    # Access token should now be revoked server-side
    me = client.get("/api/v1/auth/me", headers=_auth(access))
    assert me.status_code == 401

    # Refresh token should now be rejected
    rf = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert rf.status_code == 401


def test_logout_with_invalid_access(client, admin_user):
    resp = client.post(
        "/api/v1/auth/logout",
        headers=_auth("garbage-access-token"),
        json={"refresh_token": "garbage"},
    )
    assert resp.status_code == 401


# ─── Session isolation (users cannot revoke each other's tokens) ─────────────

def test_other_user_session_unaffected_by_logout(client, admin_user, patient_user):
    a_admin, r_admin = _login_tokens(client, "t_admin@test.com", "Admin@1234")
    a_patient, _ = _login_tokens(client, "t_patient@test.com", "Patient@1234")

    # Admin logs out -> only admin's tokens revoked
    client.post("/api/v1/auth/logout", headers=_auth(a_admin), json={"refresh_token": r_admin})
    assert client.get("/api/v1/auth/me", headers=_auth(a_admin)).status_code == 401
    # Patient's session still valid
    assert client.get("/api/v1/auth/me", headers=_auth(a_patient)).status_code == 200


def test_admin_cannot_revoke_other_token_via_logout(client, admin_user, patient_user):
    # Admin POSTs patient's refresh token to logout endpoint. Endpoint revokes only
    # tokens for the authenticated user (admin). Patient's token must remain valid.
    a_patient, r_patient = _login_tokens(client, "t_patient@test.com", "Patient@1234")
    a_admin, _ = _login_tokens(client, "t_admin@test.com", "Admin@1234")

    client.post(
        "/api/v1/auth/logout", headers=_auth(a_admin), json={"refresh_token": r_patient}
    )
    # Patient's access token still valid (only admin's access token was revoked)
    assert client.get("/api/v1/auth/me", headers=_auth(a_patient)).status_code == 200


# ─── Password change (positive + negative) ────────────────────────────────────

def test_change_password_success(client, patient_ready):
    access, refresh = _login_tokens(client, "t_patient@test.com", "Patient@1234")
    resp = client.post(
        "/api/v1/auth/change-password",
        headers=_auth(access),
        json={"old_password": "Patient@1234", "new_password": "NewPatient@99"},
    )
    assert resp.status_code == 200

    # Old refresh tokens for this user are now revoked
    rf = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert rf.status_code == 401

    # Login works with new password
    assert _login(client, "t_patient@test.com", "NewPatient@99").status_code == 200


def test_change_password_wrong_current(client, patient_ready):
    access, _ = _login_tokens(client, "t_patient@test.com", "Patient@1234")
    resp = client.post(
        "/api/v1/auth/change-password",
        headers=_auth(access),
        json={"old_password": "TotallyWrong", "new_password": "Whatever@99"},
    )
    assert resp.status_code == 400


def test_change_password_weak_new(client, patient_ready):
    access, _ = _login_tokens(client, "t_patient@test.com", "Patient@1234")
    resp = client.post(
        "/api/v1/auth/change-password",
        headers=_auth(access),
        json={"old_password": "Patient@1234", "new_password": "weak"},
    )
    assert resp.status_code == 422  # validation error


def test_change_password_unauthenticated(client):
    resp = client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "X", "new_password": "Y@123456"},
    )
    assert resp.status_code == 401


def test_change_password_does_not_leak_hash(client, patient_ready):
    access, _ = _login_tokens(client, "t_patient@test.com", "Patient@1234")
    resp = client.post(
        "/api/v1/auth/change-password",
        headers=_auth(access),
        json={"old_password": "Patient@1234", "new_password": "Another@1234"},
    )
    assert resp.status_code == 200
    assert "successfully" in resp.json().get("message", "").lower()
    # The raw response must not contain the new password or a bcrypt hash
    assert "Another@1234" not in resp.text


def test_login_after_password_change_with_old_password_fails(client, patient_ready):
    access, _ = _login_tokens(client, "t_patient@test.com", "Patient@1234")
    client.post(
        "/api/v1/auth/change-password",
        headers=_auth(access),
        json={"old_password": "Patient@1234", "new_password": "Rotated@123"},
    )
    # Old password no longer works
    assert _login(client, "t_patient@test.com", "Patient@1234").status_code == 401
    assert _login(client, "t_patient@test.com", "Rotated@123").status_code == 200
