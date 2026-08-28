# MedCore HMS

A modern hospital management system built with React 18 + TypeScript (frontend) and FastAPI + SQLAlchemy 2.0 (backend).

---

## Project Overview

MedCore HMS is a hospital management system designed to replace a legacy Django application with a modern, type-safe, async-first architecture.

**Current Scope (Foundation — Phase 1–2):**
- JWT authentication with access/refresh token rotation
- Role-based access control foundation (Admin, Doctor, Patient roles)
- Structured logging with request correlation IDs
- Database migration infrastructure (Alembic)
- Quality gates: Ruff, Mypy, Pytest in CI
- Health monitoring endpoint
- React + Vite frontend with Tailwind CSS

**Not Yet Implemented (Upcoming Phases):**
- Patient/Doctor/Appointment CRUD (Phase 3–4)
- Dashboard analytics & charts
- Discharge/billing workflows
- Real-time notifications, telemedicine, SMS/email reminders

---

## Architecture

```
medcore-hms/
├── frontend/                 # React 18 + TypeScript + Vite
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   └── layout/       # DashboardLayout with collapsible sidebar
│   │   ├── pages/            # Page components (login, register, dashboard stubs)
│   │   ├── services/         # Axios API client with token interceptors
│   │   ├── store/            # Zustand auth store (persisted)
│   │   └── styles/           # Tailwind global styles
│   └── Dockerfile
│
├── backend/                  # FastAPI + SQLAlchemy 2.0 Async
│   ├── app/
│   │   ├── api/v1/           # Versioned REST endpoints
│   │   │   └── endpoints/    # auth (login, register, refresh, logout, password change)
│   │   ├── core/             # Config, Database, Security, Logging, Enums
│   │   ├── models/           # SQLAlchemy ORM models (User, Doctor, Patient, Appointment, etc.)
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── services/         # Business logic (AuthService, UserService)
│   ├── main.py               # FastAPI app with lifespan, CORS, router
│   ├── requirements.txt
│   └── Dockerfile
│
├── alembic/                  # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 79c551ff8c41_baseline_schema.py  # Baseline: 8 tables
│
├── .github/workflows/ci.yml  # CI pipeline (Ruff, Mypy, Pytest, Frontend build)
├── docker-compose.yml        # Full stack (PostgreSQL, Redis, Backend, Frontend)
└── README.md
```

### Data Flow

```
Browser (React + TypeScript)
    │
    ▼
REST API (FastAPI)
    │
    ▼
Service Layer (AuthService, UserService)
    │
    ▼
SQLAlchemy 2.0 Async ORM
    │
    ▼
PostgreSQL (production) / SQLite (dev/test)
```

**Supporting Infrastructure:**
- Redis: Caching & session store (configured, not yet used by Foundation)
- Alembic: Schema migrations
- Docker Compose: Local full-stack deployment
- GitHub Actions: CI pipeline

---

## Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend Framework | React | 18 |
| Language | TypeScript | 5.x |
| Build Tool | Vite | 6.x |
| Styling | Tailwind CSS | 4.x |
| State Management | Zustand | 5.x |
| HTTP Client | Axios | 1.x |
| Backend Framework | FastAPI | 0.115.x |
| ORM | SQLAlchemy | 2.0.x |
| Validation | Pydantic | 2.10.x |
| Auth | Python-JOSE (JWT) + Passlib/bcrypt | 3.3.x / 1.7.x |
| ASGI Server | Uvicorn | 0.32.x |
| Database (Prod) | PostgreSQL | 16+ |
| Database (Dev/Test) | SQLite + aiosqlite | 3.x / 0.20.x |
| Migrations | Alembic | 1.19.x |
| Linting | Ruff | 0.16.x |
| Type Checking | Mypy | 2.3.x |
| Testing | Pytest | 8.3.x |
| Containerization | Docker Compose | v2 |

---

## Current Implementation Status

### ✅ Implemented (Foundation — Phase 1–2)

**Authentication & Security**
- JWT access tokens (15 min) + refresh tokens (7 days) with rotation
- Refresh token reuse detection & revocation
- Token blacklist for logout
- Password hashing with bcrypt
- Password change with current-password verification
- Role-based access control: `Admin`, `Doctor`, `Patient` enums

**Architecture & Core**
- Async SQLAlchemy 2.0 with session dependency injection
- Alembic baseline migration (`79c551ff8c41`) — 8 tables
- Structured JSON logging (`log.py`) with request correlation IDs
- Centralized enums (`enums.py`): `UserRole`, `AppointmentStatus`, `AuditAction`, `Department`
- Pydantic schemas for auth (`LoginRequest`, `PasswordChange`, `Token`, `TokenRefresh`)

**Quality Gates & CI**
- GitHub Actions workflow (`.github/workflows/ci.yml`)
- Ruff linting (line-length 100, targeted rules)
- Mypy type checking (Foundation-scoped: config, log, security, database, schemas)
- Pytest with isolated SQLite test database
- Frontend: TypeScript + Vite production build

**Health & Operations**
- `/health` endpoint — returns `{status, version, service}`
- Docker Compose for local full-stack (PostgreSQL, Redis, Backend, Frontend)

---

### ⏳ Not Yet Implemented (Planned Phases)

| Phase | Scope | Status |
|-------|-------|--------|
| **Phase 3** | Security hardening (headers, middleware), session cleanup, RBAC enforcement, discharge/dashboard endpoints | Upcoming |
| **Phase 4** | Patient/Doctor/Appointment CRUD, pagination, scheduling, audit logs, conflict detection | Upcoming |
| **Phase 5** | Frontend ESLint, UI pagination controls, doctor/patient pages, rate limiting, password reset UI | Not started |

---

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for full-stack)
- PostgreSQL 16+ (production)

### Environment Variables

**Backend** (`backend/.env` — copy from `backend/.env.example`):
```bash
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=sqlite+aiosqlite:///./medcore_hms.db
# Production: postgresql+asyncpg://user:pass@localhost/medcore_hms
DEBUG=true
ENVIRONMENT=development
```

**Frontend** (`frontend/.env` — copy from `frontend/.env.example`):
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Backend (Local)

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (creates local SQLite DB)
alembic upgrade head

# Start development server
uvicorn main:app --reload --port 8000

# API docs: http://localhost:8000/api/docs
# Health:    http://localhost:8000/health
```

### Frontend (Local)

```bash
cd frontend

# Install dependencies
npm ci

# Start dev server
npm run dev

# App: http://localhost:5173
```

### Full Stack (Docker)

```bash
# From repo root
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

docker-compose up -d

# Frontend: http://localhost
# API:      http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Running Tests & Checks

**Backend:**
```bash
cd backend

# Lint
ruff check app tests

# Type check
mypy

# Tests (18 auth tests)
pytest tests/ -v

# All checks
ruff check app tests && mypy && pytest tests/ -q
```

**Frontend:**
```bash
cd frontend

# TypeScript check
npx tsc --noEmit

# Production build
npm run build
```

**Alembic (Database):**
```bash
cd backend

# Check current revision
alembic current

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade one revision
alembic downgrade -1
```

---

## CI Pipeline

**GitHub Actions** (`.github/workflows/ci.yml`)

| Job | Steps |
|-----|-------|
| **Backend** | `ruff check` → `mypy` → `pytest tests/` |
| **Frontend** | `npm ci` → `npm run build` (includes `tsc`) |

Runs on: push to `main`/`develop`, all pull requests.

---

## Security

**Implemented in Foundation:**
- JWT authentication with short-lived access tokens + rotating refresh tokens
- Refresh token reuse detection (invalidates session on reuse)
- Token blacklist for explicit revocation (logout)
- Password hashing via bcrypt (cost factor 12)
- Role-based access control foundation (`UserRole` enum, dependency guards)
- Input validation via Pydantic schemas
- SQL injection protection via SQLAlchemy ORM
- CORS configured with explicit allowed origins

**Deferred / Not Yet Implemented:**
- Security headers middleware (Phase 3)
- Rate limiting (requires Redis integration decision)
- Password reset flow (documented in `docs/SECURITY.md`, not implemented)
- Account lockout / brute-force protection
- Audit logging for security events (Phase 4)

---

## Documentation

| File | Purpose |
|------|---------|
| `docs/ARCHITECTURE.md` | System architecture, data flow, design decisions |
| `docs/RBAC.md` | Role-based access control matrix & permissions |
| `docs/SECURITY.md` | Security model, token lifecycle, threat model, password reset workflow |
| `docs/REMAINING_PHASE_1_4_WORK.md` | Phase 1–4 task reconciliation & deferral rationale |
| `UPGRADE_ROADMAP.md` | Original phase-by-phase upgrade plan |

---

## Roadmap

- [x] **Phase 1** — Authentication & RBAC Foundation
- [x] **Phase 2** — Architecture, Migrations, Logging, CI
- [ ] **Phase 3** — Security Hardening & RBAC Enforcement
- [ ] **Phase 4** — Core Hospital Domain (Patients, Doctors, Appointments)
- [ ] **Phase 5** — Frontend Polish, ESLint, Rate Limiting, Password Reset UI

---

## License

Internal project — not licensed for public distribution.