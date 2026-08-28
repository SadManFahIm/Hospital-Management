# MedCore HMS — Security Design & Decisions

This document describes the authentication/authorization architecture, the
security controls in place, and the explicit product/security decisions made
during Phase 3. It is a living record; update it when behavior changes.

## Threat model (in scope, current)

- Unauthenticated callers must not reach protected resources.
- A user must not access another user's or admin-only resources (IDOR/BOLA).
- A stolen access token is short-lived (30 min); a stolen refresh token is
  revocable and single-use-promoted (rotation + reuse detection).
- Passwords are hashed with bcrypt and never stored or returned in plaintext.

Out of scope (documented as future work, not implemented): rate limiting,
password reset flows, account lockout, RBAC enforcement as a single
policy layer, `token_version`, JWT `iss`/`aud` claims, HIPAA/GDPR compliance.

## Token lifecycle

- **Access token**: JWT, `HS256`, 30 min TTL (`ACCESS_TOKEN_EXPIRE_MINUTES`),
  claims `sub` (user id), `role`, `email`, `type="access"`, `jti`, `exp`.
- **Refresh token**: JWT, 7 day TTL (`REFRESH_TOKEN_EXPIRE_DAYS`),
  `type="refresh"`, `jti`. Each refresh token is backed by a `RefreshSession`
  row (single use / rotation).
- **Validation** (`decode_token` / `get_current_user`): signature, `exp`,
  claim `type`, blacklist (`token_blacklist`), user `is_active`.
- **Authorization is always re-derived from the DB user**, never from the
  `role` claim in a token — token forging of the role claim does not grant
  privileges.
- **Type separation**: access tokens are rejected at the refresh endpoint and
  refresh tokens are rejected at protected endpoints.

### Rotation & reuse detection (`AuthService.refresh`)

Every refresh issues a new pair and revokes the presented refresh session.
Presenting a previously rotated (already consumed) refresh token is treated as
reuse: all of the user's refresh sessions are revoked server-side and the
violation is logged (`refresh_token_reuse_detected`).

### Logout & revocation

- `POST /auth/logout` blacklists the presented token and revokes its refresh
  session. Idempotent.
- Password change (`/auth/change-password`) calls
  `revoke_all_user_sessions` — all refresh sessions are revoked, so no new
  access tokens can be minted from a pre-change refresh token.
- Blacklist stores revoked tokens until `expires_at`; refresh reuse triage
  treats tokens not found in the session table as revoked.

### Session/token housekeeping

`AuthService.cleanup_expired_sessions` deletes **expired** refresh sessions and
**expired** blacklist records only. It **keeps** revoked-but-unexpired refresh
sessions (their presence is required for reuse detection within a token's
validity window) and unexpired blacklist entries. The cleanup runs once at
startup and then on a periodic background task every
`CLEANUP_INTERVAL_SECONDS` (default 3600s), scheduled in the app lifespan
(`main.py`). Deleting expired rows is safe: they fail `exp` validation on any
decode attempt regardless.

## Access-token revocation on password change (decision 3.3)

**Chosen: current behavior.** Changing the password revokes all *refresh*
sessions immediately, so an attacker holding the long-lived credential is cut
off. Any access token already issued to an attacker remains valid for at most
the 30-minute TTL. This bounded window is accepted for the current threat model.

Rationale: access tokens are opaque and short-lived; we cannot enumerate active
access tokens to blacklist them. Adding a per-user `token_version` claim would
allow instant invalidation of all access tokens, but requires a migration and
re-issuance logic. **Future option:** add `token_version` to `User`, include it
as a claim, and reject tokens whose version is stale; bump it on password change
or force-logout.

## RBAC model (decision 3.4)

Central helpers in `app/core/security.py`:
`require_permission(*perms)`, `require_admin`, `require_doctor`. Most
admin/doctor/patient gates go through these. Endpoints that perform
**resource-level ownership checks** (e.g. a patient only reads their own
appointments, a doctor only reads their own patients) do so inline because the
checks depend on the specific resource and owner — they cannot be expressed by a
stateless role dependency and are deliberately **not** abstracted into a
one-size-fits-all policy layer. Each such check is scoped to the authenticated
user's own records (see ARCHITECTURE.md).

Authorization failures are raised as `HTTPException` with the appropriate
status code (401 for unauthenticated, 403 for forbidden).

## Password security (decision 3.8)

- bcrypt via passlib; stored as `hashed_password`, never logged.
- Strength policy enforced on registration and password change
  (min length + upper/lower/digit/special), validated in schemas.
- No endpoint returns `hashed_password` or raw passwords (see sensitive-field
  exclusion, below).
- **Future requirement, not implemented:** self-service password reset with
  expiry/link; email verification on registration.

## Doctor approval flow (decision 3.9)

- Registration (`/auth/register`) only ever creates patients.
- Doctors are created by an admin; a new doctor starts with
  `is_approved=False` until an admin runs `POST /doctors/{id}/approve`.
- **Chosen:** login does **not** gate on `is_approved`. A doctor created by an
  admin can authenticate and work before approval; approval controls public
  visibility and bookability rather than access. This is a business decision,
  not a security boundary failure — unapproved doctors are admin-created, not
  self-registered.
- **Future option:** `get_current_user` could reject `is_approved=False`
  accounts if product wants approval to gate access. Requires a product
  decision; not changed silently.

## API hardening

- **Security headers** (`SecurityHeadersMiddleware` in `app/core/middleware.py`):
  `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
  `Referrer-Policy: no-referrer`, `X-Permitted-Cross-Domain-Policies: none`,
  and `Strict-Transport-Security` (HSTS) added only when the request arrived
  over HTTPS.
- **CORS**: specific origins with `allow_credentials=True`; no wildcard
  origin with credentials.
- **Sensitive-field exclusion**: all response schemas (`UserResponse`,
  `PatientResponse`, `DoctorResponse`, `DischargeResponse`, etc.) exclude
  `hashed_password`/tokens. Discharge endpoints serialize through the
  `DischargeResponse` controlled schema (never raw ORM) and eager-load nested
  relationships to avoid lazy-loading after session close.
- **No secrets in logs**: `RequestLoggingMiddleware` never logs
  Authorization headers, bodies, tokens, or passwords.
- **Rate limiting** is **future work** (in-memory limiting is unreliable across
  workers; a Redis-backed limiter is a future dependency decision).

## Regression coverage

See `backend/tests/`:
- `test_auth.py`, `test_rbac.py` — auth negatives, role access, IDOR/BOLA.
- `test_session_cleanup.py` — housekeeping deletes only expired records and
  preserves revoked-but-unexpired refresh sessions.
- `test_security_hardening.py` — expired/wrong-type/malformed tokens,
  sensitive-field exclusion, security headers, password strength, discharge
  controlled-schema serialization.