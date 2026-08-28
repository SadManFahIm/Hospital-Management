# RBAC - Role-Based Access Control Matrix

This document is the authoritative reference for the authorization model
(currently Foundation — authentication layer only).

---

## Roles

| Role | Description |
|------|-------------|
| `admin`  | Full system administration (future phases). |
| `doctor` | Clinical staff (future phases). |
| `patient` | End users (future phases). |

Roles are stored server-side as `UserRole` enum (`ADMIN`, `DOCTOR`, `PATIENT`)
in `backend/app/core/enums.py` and referenced by `backend/app/core/security.py`.

---

## Current Implementation (Foundation)

The Foundation branch implements only the **authentication layer**.
Full RBAC enforcement on resource endpoints (Patients, Doctors, Appointments)
is deferred to Phase 3–4.

### What Exists Now

- **Auth endpoints** (`/api/v1/auth/*`):
  - `POST /login` — authenticate, returns access + refresh token
  - `POST /register` — register new patient (role=patient)
  - `POST /refresh` — rotate refresh token
  - `POST /logout` — revoke refresh session + blacklist access token
  - `POST /change-password` — change password with current-password check

- **Token lifecycle:**
  - Access token: 15 min, signed JWT (HS256)
  - Refresh token: 7 days, stored in `refresh_sessions` table
  - Rotation: single-use; reuse revokes all user sessions
  - Logout: blacklists access token JTI in `token_blacklist`

- **RBAC foundation:**
  - `UserRole` enum (`ADMIN`, `DOCTOR`, `PATIENT`) in `app/core/enums.py`
  - `require_role`, `require_permission` helpers in `security.py`
  - Dependency guards: `get_current_user`, `require_admin`, `require_doctor`

---

## Planned Permission Matrix (Phase 3–4)

| Permission | Admin | Doctor | Patient |
|-----------|:-----:|:------:|:-------:|
| `users.read`          | ✔ | ✔ | – |
| `users.create/update/delete` | ✔ | – | – |
| `patients.read`       | ✔ | ✔ | ✔ (own only) |
| `patients.create`     | ✔ | – | – |
| `patients.update`     | ✔ | ✔ (assigned) | ✔ (own only) |
| `patients.delete`     | ✔ | – | – |
| `patients.admit`      | ✔ | – | – |
| `patients.discharge`  | ✔ | – | – |
| `doctors.read`        | ✔ | ✔ | ✔ |
| `doctors.create/delete` | ✔ | – | – |
| `doctors.update`      | ✔ | ✔ (own profile) | – |
| `doctors.approve`     | ✔ | – | – |
| `appointments.read`   | ✔ | ✔ (own) | ✔ (own) |
| `appointments.create` | ✔ | ✔ | ✔ (own) |
| `appointments.update` | ✔ | ✔ (own) | ✔ (own) |
| `appointments.delete` | ✔ | – | – |
| `appointments.cancel` | ✔ | ✔ (own) | ✔ (own) |

> **Note:** The above matrix is the design target for Phase 3–4.
> Current Foundation branch does not implement resource endpoints yet.

---

## Resource-Level Authorization (IDOR / BOLA) — Planned

When resource endpoints are implemented (Phase 3–4), object ownership will be
enforced server-side:

- **Patients:** a `patient` may only read/update their own `Patient` record
  (`Patient.user_id == current_user.id`).
- **Appointments:** a `patient` may only read/update appointments where
  `appointment.patient.user_id == current_user.id`; a `doctor` only where
  `appointment.doctor.user_id == current_user.id`.
- **Doctors:** a `doctor` may update only their own profile
  (`Doctor.user_id == current_user.id`).
- Booking scope: a `patient` cannot create an appointment for another patient
  (`403`).

---

## Auth Behavior (Current)

- Missing / invalid / expired access token → **401**
- Authenticated but missing required role/permission or resource ownership → **403**
- Refresh-token flow: single-use rotation with reuse detection (reuse revokes
  all of the user's sessions)

---

## Verification Status (Foundation)

- [x] Auth endpoints: login, register, refresh, logout, password change
- [x] Token lifecycle: rotation, reuse detection, revocation, blacklist
- [x] RBAC foundation: `UserRole` enum, `require_role`, `require_permission`
- [x] Dependencies: `get_current_user`, `require_admin`, `require_doctor`
- [x] Auth tests: 18 tests passing (`backend/tests/test_auth.py`)
- [x] Application starts; all auth routes registered
- [x] Type checking passes (Foundation scope)
- [x] CI pipeline configured

---

## Next Steps (Phase 3–4)

- Implement Patients/Doctors/Appointments CRUD endpoints
- Enforce resource ownership (IDOR/BOLA protection) at endpoint/service layer
- Add security headers middleware
- Add audit logging for security events
- Expand RBAC test coverage (`test_rbac.py`)