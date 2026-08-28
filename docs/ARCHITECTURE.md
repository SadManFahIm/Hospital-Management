# Architecture — MedCore HMS (Foundation — Phase 1–2)

High-level architecture and operational guidance for the MedCore Hospital
Management System. This document covers the current state after **Phase 1–2**
(foundation: authentication, Alembic migrations, structured logging, CI).

---

## Overview

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite, React Router, TanStack Query, Zustand, Tailwind CSS |
| Backend | Python 3.11 + FastAPI (async), SQLAlchemy 2.0 (async) ORM |
| Database | SQLite (dev/test) via `aiosqlite`; PostgreSQL (production, `asyncpg`) |
| Auth | JWT access + refresh tokens (python-jose), server-side session/blacklist tracking |
| Migrations | Alembic |
| Logging | JSON structured logging via stdlib `logging` + request-id contextvar |
| Quality | Ruff (lint), Mypy (type-check), Pytest, tsc + Vite build, GitHub Actions CI |

Monorepo layout:

```
backend/             FastAPI application
  app/core/          config, security, database, enums, logging
  app/models/        SQLAlchemy models (authoritative in app/models/__init__.py)
  app/schemas/       Pydantic schemas
  app/services/      business / service layer
  app/api/v1/        API routers + endpoint dependencies
  alembic/           Alembic migration environment + versions
  tests/             pytest suite (isolated SQLite test DB)
frontend/            React + Vite application
docs/                RBAC matrix, architecture
.github/workflows/   CI pipeline
```

---

## Backend

FastAPI application in `backend/main.py`. On startup (lifespan):

- `setup_logging()` configures JSON logging.
- Request logging middleware attached for per-request access logs + request IDs.
- `create_tables()` runs **only when `ENVIRONMENT != "production"`** (dev/test).
  Production schema is managed exclusively by Alembic.

### Application layers

- **Routers** (`app/api/v1/endpoints/`) — HTTP concerns, request/response wiring,
  thin. Auth + RBAC enforced via FastAPI dependencies.
- **Services** (`app/services/`) — business logic. Eager-load relationships
  (`selectinload`) so serialization never triggers lazy loads after the async
  session closes.
- **Schemas** (`app/schemas/`) — Pydantic v2 request/response models.
- **Models** (`app/models/__init__.py`) — the authoritative SQLAlchemy metadata
  (all tables, including `refresh_sessions` and `token_blacklist`). The
  `models/user.py`, `doctor.py`, `patient.py`, `appointment.py` files are empty
  placeholders; do not rely on them.

### Configuration (`app/core/config.py`)

`pydantic-settings`-based. Key values: `DATABASE_URL` (async URL), `ENVIRONMENT`
(default `production`), `DEBUG`. `.env` in `backend/` supplies local SQLite URL;
environment variables take precedence over `.env`.

### Database & migrations

- Async engine created in `app/core/database.py` (`Base` = `DeclarativeBase`).
- **Alembic** is the single source of truth for schema in all environments:
  - `alembic.ini` + `alembic/env.py` derive a **sync** URL from
    `settings.DATABASE_URL` (e.g. `sqlite+aiosqlite://` → `sqlite://`,
    `postgresql+asyncpg://` → `postgresql://`) and register every model via
    `import app.models` so autogenerate sees the full `Base.metadata`.
  - **Creating/Altering schema:** `alembic revision --autogenerate -m "..."`,
    review the diff, then `alembic upgrade head`.
  - **Fresh DB:** `alembic upgrade head` builds all 8 tables + `alembic_version`.
  - **Existing DB (schema already present):** `alembic stamp head` records the
    current revision without running DDL (non-destructive; preserves data).
  - Baseline migration `79c551ff8c41` captures the initial 8 tables:
    `users`, `doctors`, `patients`, `appointments`, `audit_logs`,
    `discharge_details`, `refresh_sessions`, `token_blacklist`.

### Authentication & authorization

- **Auth:** access token (short-lived) + refresh token (rotated; stored in
  `refresh_sessions`). Reuse detection revokes all sessions. Logout blacklists
  the access token JTI in `token_blacklist` (server-side invalidation).
- **RBAC:** roles (`ADMIN`/`DOCTOR`/`PATIENT`, `UserRole` in `app/core/enums.py`)
  map to a permission registry (`PERMISSIONS`, `require_permission`,
  `user_has_permission`, `require_role`). HTTPBearer uses `auto_error=False` so
  missing credentials yield **401** (not 403). See `docs/RBAC.md`.

### Logging (`app/core/log.py`)

JSON structured logs (timestamp ISO-8601 UTC, level, logger, message,
`request_id`, `_extra`, exception). Request middleware:
- Generates a UUID request id and sets the `request_id` contextvar.
- Logs one access line per request (method, path, status, duration_ms).
- Logs unhandled exceptions server-side **without** leaking details to clients.
- **Never logs** Authorization headers, tokens, passwords, or request bodies.
- Security-event logs in the auth flow carry user identifiers only.

---

## Frontend

React + Vite SPA in `frontend/`. `npm run build` runs `tsc && vite build`
(type-check + production build). Auth wiring lives in
`frontend/src/services/api.ts` and `frontend/src/store/authStore.ts`.

---

## Testing & quality gates

Run from `backend/` (back) or `frontend/` (front):

| Gate | Command | Expectation (Foundation) |
|---|---|---|
| Backend tests | `pytest tests/ -q` | 18 passed (auth suite) |
| Backend lint | `ruff check .` | All checks passed |
| Backend type-check | `mypy` | Success (scoped to core + schemas) |
| Frontend build | `npm run build` | tsc + vite pass |

- Tests use a dedicated SQLite test DB (`tests/test_medcore_hms.db`) created
  automatically; dev/production data is never touched.
- CI (`.github/workflows/ci.yml`) runs backend (pytest + ruff + mypy) and
  frontend (npm run build) on every push/PR. No secrets or DB services required.

### Mypy scope (documented)

Mypy is scoped to the Foundation infrastructure core + schemas
(`config, log, security, database, schemas`).
`app/models`, `app/services`, and `app/api` currently use the classic SQLAlchemy
`Column`-attribute style whose mapper types conflict with instance assignments;
migrating them to the `Mapped[...]` annotation style is a **deferred**,
cross-cutting refactor. `follow_imports = "silent"` supplies type info from those
modules without reporting their (deferred) errors.

### Ruff choices (documented)

- `B008` ignored — FastAPI idiom is `Depends()` in argument defaults.
- `B905` ignored.
- `alembic/versions/*` auto-generated migrations excluded from `E/W/I`.
- `ruff format` is configured but not enforced project-wide (avoids churning
  pre-existing files); an opt-in follow-up.

---

## Known debt / deferred

- ORM `Mapped[...]` typing refactor (widens mypy coverage to services/models/api).
- `ruff format` enforcement (opt-in, avoids broad churn).
- Frontend ESLint config (Phase 5.15; no `eslint` config in repo yet).
- Rate limiting (Redis-backed; requires a dependency decision), password reset,
  account lockout, `token_version` per-user access-token invalidation.
- Scheduling enrichment: working hours / availability / holidays / doctor leave /
  recurring availability / override rules (foundation helpers exist in
  `app/core/scheduling.py`).
- Splitting `models/__init__.py` / `schemas/__init__.py` into separate files
  (the empty per-file placeholders remain for a future split; the monolithic
  `__init__.py` files are authoritative).

A full, current Phase 1–4 status matrix is maintained in
`docs/REMAINING_PHASE_1_4_WORK.md`. See `UPGRADE_ROADMAP.md` for the phased
plan, acceptance criteria, and verification notes.