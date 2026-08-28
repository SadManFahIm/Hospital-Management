"""
MedCore HMS - Hospital Management System
Modern FastAPI Backend with JWT Authentication & RBAC
"""

import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, create_tables
from app.core.log import setup_logging
from app.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.services.auth_service import AuthService
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Centralized structured logging (call before any handlers depend on it).
setup_logging(debug=settings.DEBUG)

logger = logging.getLogger("medcore.main")


async def _run_cleanup_once():
    """Remove expired refresh sessions and expired token-blacklist records."""
    async with AsyncSessionLocal() as db:
        try:
            await AuthService.cleanup_expired_sessions(db)
        except Exception:
            logger.exception("session/token cleanup failed")


async def _cleanup_loop():
    """Periodic housekeeping for expired sessions/blacklist records."""
    while True:
        await asyncio.sleep(settings.CLEANUP_INTERVAL_SECONDS)
        await _run_cleanup_once()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.

    Database schema is managed by Alembic migrations in production
    (`alembic upgrade head`). Automatic table creation is limited to local
    development, so production schema is never silently changed at startup.

    Session/token housekeeping runs once at startup and then on a periodic
    background task. It only deletes *expired* refresh sessions and expired
    token-blacklist records; revoked-but-unexpired refresh sessions are kept so
    refresh-token reuse detection keeps working within a token's validity window.
    """
    if settings.ENVIRONMENT.lower() != "production":
        await create_tables()
    await _run_cleanup_once()
    cleanup_task = asyncio.create_task(_cleanup_loop())
    try:
        yield
    finally:
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task


app = FastAPI(
    title="MedCore HMS API",
    description="Hospital Management System - Modern REST API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Request correlation id + safe access logging.
app.add_middleware(RequestLoggingMiddleware)

# Safe, standard security headers (HSTS only over HTTPS).
app.add_middleware(SecurityHeadersMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0", "service": "MedCore HMS"}
