# RBAC - Role-Based Access Control Matrix

This document is the authoritative reference for the authorization model
(self-service + admin) across the **Patients**, **Doctors**, and
**Appointments** modules. The backend is the sole authority for authorization;
frontend checks (if any) are for UX only and never trust the client.

## Roles

| Role | Description |
|------|-------------|
| `admin`  | Full system administration. Elevated create/update/delete/approve/admit/discharge rights. |
| `doctor` | Clinical staff. Read patient/doctor/appointment data, update own profile, manage assigned patients, view own appointments. |
| `patient` | End users. Read doctors, manage only their **own** patient record and appointments. |

Roles are stored server-side as `UserRole` enum (`ADMIN`, `DOCTOR`, `PATIENT`)
and enforced via the centered permission registry in
`backend/app/core/security.py` (`PERMISSIONS`, `user_has_permission`,
`require_permission`, `require_role`).

## Permission Registry (backend/app/core/security.py)

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
| `billing.read/create` | ✔ | – | – |
| `discharge.read/create` | ✔ | – | – |
| `reports.read/export`, `audit_logs.read` | ✔ | – | – |

> `doctors.read` and `doctors.create` permission checks are applied with
> `require_permission(...)`. Resource ownership is enforced at the endpoint /
> service layer in addition to the registry (see below).

## Endpoint Matrix

### Patients (`/api/v1/patients`)

| Endpoint | Method | Dependency | Access |
|----------|--------|-----------|--------|
| `/` (list) | GET | `get_current_user` | admin/doctor: all; patient: own record only |
| `/me` | GET | `get_current_user` | any; returns caller's own patient record |
| `/{id}` | GET | `get_current_user` | patient: own only (403 otherwise); doctor/admin: any |
| `/` (create) | POST | `patients.create` | admin |
| `/{id}` | PUT | `get_current_user` + owner check | admin; patient-owner; assigned doctor |
| `/{id}` | DELETE | `patients.delete` | admin |
| `/{id}/admit` | PATCH | `patients.admit` | admin |
| `/{id}/discharge` | PATCH | `patients.discharge` | admin |

### Doctors (`/api/v1/doctors`)

| Endpoint | Method | Dependency | Access |
|----------|--------|-----------|--------|
| `/` (list) | GET | `doctors.read` | admin/doctor/patient |
| `/{id}` | GET | `doctors.read` | admin/doctor/patient |
| `/` (create) | POST | `doctors.create` | admin |
| `/{id}` | PUT | `get_current_user` + owner check | admin; doctor own profile |
| `/{id}/approve` | PATCH | `doctors.approve` | admin |
| `/{id}` | DELETE | `doctors.delete` | admin |
| `/{id}/patients` | GET | `require_doctor` | admin/doctor; doctor sees own patients only |

### Appointments (`/api/v1/appointments`)

| Endpoint | Method | Dependency | Access |
|----------|--------|-----------|--------|
| `/` (list) | GET | `get_current_user` | admin: all; doctor: own; patient: own |
| `/{id}` | GET | `get_current_user` + owner check | patient/doctor: own; admin: any |
| `/` (create) | POST | `get_current_user` + patient scope | admin: any; doctor: any; patient: own only |
| `/{id}` | PATCH | `get_current_user` + owner check | admin: any; patient/doctor: own |
| `/{id}` | DELETE | `get_current_user` | admin only |

## Resource-Level Authorization (IDOR / BOLA)

Object ownership is enforced server-side for every record the current user is
allowed to partially access:

- **Patients:** a `patient` may only read/update their own `Patient` record
  (`Patient.user_id == current_user.id`). A patient who knows another
  patient's ID is rejected with `403`.
- **Appointments:** a `patient` may only read/update appointments where
  `appointment.patient.user_id == current_user.id`; a `doctor` only where
  `appointment.doctor.user_id == current_user.id`. Cross-owner access ⇒ `403`.
- **Doctors:** a `doctor` may update only their own profile
  (`Doctor.user_id == current_user.id`); the `/{id}/patients` listing returns
  `[]` if the doctor requests another doctor's patient list.
- Booking scope: a `patient` cannot create an appointment for another patient
  (`403`).

## Auth Behavior

- Missing / invalid / expired access token → **401**.
- Authenticated but missing required role/permission or resource ownership → **403**.
- Refresh-token flow: single-use rotation with reuse detection (reuse revokes
  all of the user's sessions). See the auth security task notes.

## Verification Status

- [x] Patients endpoints verified
- [x] Doctors endpoints verified
- [x] Appointments endpoints verified
- [x] Imports verified (app starts, all routes registered)
- [x] Auth dependencies verified
- [x] RBAC matrix documented (this file)
- [x] RBAC tests added (`backend/tests/test_rbac.py`)
- [x] Unauthorized access tests pass
- [x] IDOR/BOLA checks pass
- [x] Existing backend tests pass (44 total)
- [ ] Lint passes (blocked: no ESLint/backend linter config in repo - see notes)
- [x] Type checking passes (frontend `tsc --noEmit`)
- [x] Application starts successfully
- [x] No auth regression remains
