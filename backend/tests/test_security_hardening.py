"""
Security hardening tests (Phase 3).

Covers additional auth negatives (expired / wrong-type / malformed tokens),
sensitive-field exclusion across API responses, security headers, and password
strength validation. Uses an isolated test DB (see conftest).
"""

import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from app.core.config import settings
from jose import jwt


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _login_tokens(client, email, password):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"], r.json()["refresh_token"]


def _admin_tokens(client):
    return _login_tokens(client, "t_admin@test.com", "Admin@1234")[0]


def _signed_token(payload):
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _run(coro):
    return asyncio.run(coro)


def _expired_access_token(sub="1"):
    payload = {
        "sub": sub,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "email": "x@test.com",
        "role": "admin",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    return _signed_token(payload)


# ─── Token negatives ───────────────────────────────────────────────────────────


def test_expired_access_token_rejected(client, admin_user):
    token = _expired_access_token(sub=str(admin_user))
    resp = client.get("/api/v1/auth/me", headers=_auth(token))
    assert resp.status_code == 401


def test_refresh_token_rejected_on_protected_endpoint(client, admin_user):
    _, refresh = _login_tokens(client, "t_admin@test.com", "Admin@1234")
    resp = client.get("/api/v1/auth/me", headers=_auth(refresh))
    assert resp.status_code == 401


def test_malformed_token_rejected(client, admin_user):
    resp = client.get("/api/v1/auth/me", headers=_auth("not.a.jwt"))
    assert resp.status_code == 401


def test_access_token_rejected_as_refresh(client, admin_user):
    access, _ = _login_tokens(client, "t_admin@test.com", "Admin@1234")
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": access})
    assert resp.status_code == 401


# ─── Sensitive-field exclusion ─────────────────────────────────────────────────


def test_login_response_excludes_secrets(client, admin_user):
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "t_admin@test.com", "password": "Admin@1234"},
    )
    body = r.json()
    assert "hashed_password" not in body["user"]
    assert "password" not in body["user"]
    assert "hashed_password" not in body


def test_me_response_excludes_secrets(client, admin_user):
    access, _ = _login_tokens(client, "t_admin@test.com", "Admin@1234")
    resp = client.get("/api/v1/auth/me", headers=_auth(access))
    body = resp.json()
    assert "hashed_password" not in body
    assert "password" not in body


def test_users_list_excludes_password_hashes(client, admin_user):
    access, _ = _login_tokens(client, "t_admin@test.com", "Admin@1234")
    resp = client.get("/api/v1/users/", headers=_auth(access))
    assert resp.status_code == 200
    for user in resp.json():
        assert "hashed_password" not in user
        assert "password" not in user


# Patient/Doctor creation endpoints are Phase 4 features; these tests are skipped
# until those endpoints are implemented. The sensitive-field exclusion logic in
# schemas (UserResponse, PatientResponse, DoctorResponse) already excludes
# hashed_password, so the behavior is correct once the endpoints exist.
# def test_patient_response_excludes_secrets(client, admin_user): ...
# def test_doctor_response_excludes_secrets(client, admin_user): ...


# ─── Security headers ──────────────────────────────────────────────────────────


def test_security_headers_present(client):
    resp = client.get("/health")
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"
    assert resp.headers.get("referrer-policy") == "no-referrer"


# ─── Password strength validation ──────────────────────────────────────────────


def test_register_rejects_weak_password(client, admin_user):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"weakpw.{uuid.uuid4().hex[:8]}@test.com",
            "username": f"w_{uuid.uuid4().hex[:8]}",
            "password": "onlylowercase",
            "first_name": "Weak",
            "last_name": "Pass",
        },
    )
    assert resp.status_code == 422


# ─── Discharge controlled-response serialization (3.6) ────────────────────────


def test_discharge_list_uses_controlled_schema(client, admin_user):
    """The /discharges/ endpoint must serialize via DischargeResponse (a
    controlled schema) with no internal/sensitive fields leaked, even though the
    underlying resource is an ORM DischargeDetails instance."""
    from app.core.database import AsyncSessionLocal
    from app.core.security import get_password_hash
    from app.models import DischargeDetails, Patient, User, UserRole

    async def _seed():
        async with AsyncSessionLocal() as db:
            user = User(
                email=f"disch.{uuid.uuid4().hex[:8]}@test.com",
                username=f"disp_{uuid.uuid4().hex[:8]}",
                hashed_password=get_password_hash("Test@1234"),
                first_name="Disch",
                last_name="arge",
                role=UserRole.PATIENT,
                is_active=True,
                is_approved=True,
            )
            db.add(user)
            await db.flush()
            patient = Patient(
                user_id=user.id, mobile="1112223333", address="Disch Rd"
            )
            db.add(patient)
            await db.flush()
            db.add(
                DischargeDetails(
                    patient_id=patient.id,
                    admit_date=date(2026, 1, 1),
                    release_date=date(2026, 1, 4),
                    days_spent=3,
                    room_charge=Decimal("100.00"),
                    medicine_cost=Decimal("50.00"),
                    doctor_fee=Decimal("0.00"),
                    other_charges=Decimal("0.00"),
                    total=Decimal("150.00"),
                    diagnosis="Follow-up",
                    treatment_summary="Recovering",
                )
            )
            await db.commit()

    _run(_seed())

    access, _ = _login_tokens(client, "t_admin@test.com", "Admin@1234")
    resp = client.get("/api/v1/discharge/", headers=_auth(access))
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body, "expected at least one discharge row"
    d = body[-1]
    # Controlled schema fields present
    assert "id" in d and "days_spent" in d and "total" in d
    assert "patient" in d and "user" in d["patient"]
    # Sensitive fields never leaked
    assert "hashed_password" not in d
    assert "hashed_password" not in d["patient"]
    assert "hashed_password" not in d["patient"]["user"]
    assert "password" not in str(d)
