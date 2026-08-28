"""
Security Utilities - JWT, Password Hashing, RBAC
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.enums import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    import uuid
    to_encode.update({"exp": expire, "type": "access", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    import uuid
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


async def revoke_token(db: AsyncSession, jti: str, token_type: str, expires_at: datetime):
    """Add a token to the server-side blacklist (e.g. on logout)."""
    from app.models import TokenBlacklist
    token = TokenBlacklist(
        jti=jti, token_type=token_type, expires_at=expires_at
    )
    db.add(token)
    await db.commit()


async def is_token_revoked(db: AsyncSession, jti: Optional[str]) -> bool:
    """Check whether a token has been blacklisted."""
    if not jti:
        return False
    from sqlalchemy import select

    from app.models import TokenBlacklist
    result = await db.execute(select(TokenBlacklist).where(TokenBlacklist.jti == jti))
    return result.scalar_one_or_none() is not None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user"""
    from app.services.user_service import UserService

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    if await is_token_revoked(db, payload.get("jti")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = await UserService.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_current_user_with_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Return (user, raw_access_token) for endpoints that must revoke the access token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_current_user(credentials=credentials, db=db)
    return user, credentials.credentials


# Permission registry: mapping of permission -> set of roles granted it.
# Least-privilege model. The backend is the authority for authorization.
PERMISSIONS: dict[str, set[UserRole]] = {
    # users
    "users.read": {UserRole.ADMIN, UserRole.DOCTOR},
    "users.create": {UserRole.ADMIN},
    "users.update": {UserRole.ADMIN},
    "users.delete": {UserRole.ADMIN},
    # patients
    "patients.read": {UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT},
    "patients.create": {UserRole.ADMIN},
    "patients.update": {UserRole.ADMIN, UserRole.DOCTOR},
    "patients.delete": {UserRole.ADMIN},
    "patients.admit": {UserRole.ADMIN},
    "patients.discharge": {UserRole.ADMIN},
    # doctors
    "doctors.read": {UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT},
    "doctors.create": {UserRole.ADMIN},
    "doctors.update": {UserRole.ADMIN, UserRole.DOCTOR},
    "doctors.approve": {UserRole.ADMIN},
    "doctors.delete": {UserRole.ADMIN},
    # appointments
    "appointments.read": {UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT},
    "appointments.create": {UserRole.ADMIN, UserRole.PATIENT},
    "appointments.approve": {UserRole.ADMIN, UserRole.DOCTOR},
    "appointments.update": {UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT},
    "appointments.delete": {UserRole.ADMIN},
    "appointments.cancel": {UserRole.ADMIN, UserRole.PATIENT, UserRole.DOCTOR},
    # billing / discharge
    "billing.read": {UserRole.ADMIN},
    "billing.create": {UserRole.ADMIN},
    "discharge.read": {UserRole.ADMIN},
    "discharge.create": {UserRole.ADMIN},
    # dashboard / reports
    "dashboard.read": {UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT},
    "reports.read": {UserRole.ADMIN},
    "reports.export": {UserRole.ADMIN},
    "audit_logs.read": {UserRole.ADMIN},
}


def user_has_permission(user, permission: str) -> bool:
    """Check whether a user's role grants a given permission."""
    if user is None:
        return False
    roles = PERMISSIONS.get(permission, set())
    return user.role in roles


def require_role(*roles: UserRole):
    """RBAC dependency - require specific role(s)"""
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return current_user
    return role_checker


def require_permission(permission: str):
    """Fine-grained RBAC dependency - require a specific permission."""
    async def permission_checker(current_user=Depends(get_current_user)):
        if not user_has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Missing permission: {permission}",
            )
        return current_user
    return permission_checker


require_admin = require_role(UserRole.ADMIN)
require_doctor = require_role(UserRole.DOCTOR, UserRole.ADMIN)
require_patient = require_role(UserRole.PATIENT)
require_any = require_role(UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT)
