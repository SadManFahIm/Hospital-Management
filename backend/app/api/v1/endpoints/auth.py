"""
Authentication Endpoints - Login, Register, Refresh Token, Logout, Password Change
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_with_token, verify_password
from app.schemas import (
    LoginRequest,
    PasswordChange,
    Token,
    TokenRefresh,
    UserCreate,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()

logger = logging.getLogger("medcore.auth")


@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token pair."""
    user = await UserService.get_user_by_email(db, credentials.email)

    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning("login_failed", extra={"_extra": {"email": credentials.email}})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        logger.warning(
            "login_failed_deactivated",
            extra={"_extra": {"email": credentials.email, "user_id": user.id}},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    tokens = await AuthService.issue_tokens(db, user)
    logger.info(
        "login_success",
        extra={"_extra": {"user_id": user.id, "role": user.role.value}},
    )
    return tokens


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new patient user."""
    existing = await UserService.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_data.role = "patient"  # Public registration is always patient
    user = await UserService.create_user(db, user_data)
    return UserResponse.model_validate(user)


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token (with rotation reuse detection)."""
    return await AuthService.refresh(db, token_data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    body: TokenRefresh,
    db: AsyncSession = Depends(get_db),
    current_user_with_token=Depends(get_current_user_with_token),
):
    """
    Logout. Revokes the presented refresh token and the current access token
    server-side. Requires a valid access token to prove identity.
    Idempotent: already-revoked tokens are handled safely.
    """
    current_user, access_token = current_user_with_token
    await AuthService.logout(db, current_user, body.refresh_token, is_access=False)
    await AuthService.logout(db, current_user, access_token, is_access=True)
    return {"message": "Successfully logged out"}


@router.post("/change-password", response_model=dict)
async def change_password(
    body: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user_with_token=Depends(get_current_user_with_token),
):
    """
    Change the current user's password. Revokes all existing refresh sessions.
    Existing access tokens are short-lived (30 min) and will naturally expire.
    """
    current_user = current_user_with_token[0]
    await AuthService.change_password(db, current_user, body.old_password, body.new_password)
    return {"message": "Password changed successfully"}
