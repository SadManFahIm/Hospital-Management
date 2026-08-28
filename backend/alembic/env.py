"""Alembic migration environment.

Wires Alembic to the application's SQLAlchemy metadata (app.core.database.Base)
and the configured DATABASE_URL (app.core.config.settings). The async URL is
converted to its sync equivalent because Alembic runs migrations with a
synchronous DBAPI driver.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make `app` importable when this file is executed.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import app.models  # noqa: F401  (register all models on Base.metadata)
from app.core.config import settings
from app.core.database import Base


def _sync_url(async_url: str) -> str:
    """Derive a synchronous SQLAlchemy URL from the async URL."""
    # e.g. postgresql+asyncpg:// -> postgresql://, sqlite+aiosqlite:// -> sqlite://
    for async_driver, sync_driver in (
        ("postgresql+asyncpg://", "postgresql://"),
        ("postgresql+psycopg://", "postgresql://"),
        ("sqlite+aiosqlite://", "sqlite://"),
        ("mysql+asyncmy://", "mysql://"),
    ):
        if async_url.startswith(async_driver):
            return async_url.replace(async_driver, sync_driver, 1)
    return async_url


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override the configured URL with the application's DATABASE_URL.
config.set_main_option("sqlalchemy.url", _sync_url(settings.DATABASE_URL))

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
