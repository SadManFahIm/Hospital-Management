"""
Test fixtures. Uses an isolated SQLite database so development data is untouched.
Environment variables are set BEFORE importing the application so the async engine
is configured against the test database.
"""

import asyncio
import os
from pathlib import Path

import pytest

# Point the app at a dedicated test database before importing app modules.
TEST_DB = Path(__file__).resolve().parent / "test_medcore_hms.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB}"
os.environ["ENVIRONMENT"] = "test"

from app.core.database import AsyncSessionLocal, create_tables  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models import User, UserRole  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from main import app  # noqa: E402
from sqlalchemy import select  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create tables in the test database once per test session."""
    async def _create():
        await create_tables()
    asyncio.run(_create())
    yield
    # Clean up test DB file after session
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(TEST_DB) + suffix)
        if p.exists():
            try:
                p.unlink()
            except OSError:
                pass


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


async def _ensure_user(email, username, password, role, approved=True, active=True):
    async with AsyncSessionLocal() as db:
        existing = await db.scalar(select(User).where(User.email == email))
        if existing:
            return existing.id
        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            first_name="Test",
            last_name="User",
            role=role,
            is_active=active,
            is_approved=approved,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user.id


@pytest.fixture(scope="session")
def admin_id():
    yield asyncio.run(_ensure_user("t_admin@test.com", "tadmin", "Admin@1234", UserRole.ADMIN))


@pytest.fixture(scope="session")
def patient_id():
    yield asyncio.run(
        _ensure_user("t_patient@test.com", "tpatient", "Patient@1234", UserRole.PATIENT)
    )


@pytest.fixture(scope="session")
def admin_user(admin_id):
    asyncio.run(_ensure_user("t_admin@test.com", "tadmin", "Admin@1234", UserRole.ADMIN))
    return admin_id


@pytest.fixture(scope="session")
def patient_user(patient_id):
    asyncio.run(_ensure_user("t_patient@test.com", "tpatient", "Patient@1234", UserRole.PATIENT))
    return patient_id
