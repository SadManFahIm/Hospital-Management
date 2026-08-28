"""
Async Database Configuration with SQLAlchemy
"""

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


# Import the model package so every model is registered on Base.metadata.
# Without this import, create_all / Alembic autogenerate would silently miss
# tables if the models had not already been imported elsewhere via side-effects.
import app.models  # noqa: E402,F401


async def create_tables():
    """Create all database tables.

    Intended ONLY for local development and isolated tests. Production schema is
    managed by Alembic migrations (`alembic upgrade head`).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
