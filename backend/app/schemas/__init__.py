"""
Pydantic Schemas for Request/Response validation
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, EmailStr, Field, validator

from app.core.enums import AppointmentStatus, UserRole

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Reusable paginated list envelope used by all list endpoints."""

    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int

# ─── Auth Schemas ──────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenRefresh(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ─── User Schemas ──────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.PATIENT

    @validator("password")
    def validate_password_strength(cls, v):
        if not any(c.islower() for c in v):
            raise ValueError("password must contain at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain at least one digit")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in v):
            raise ValueError("password must contain at least one special character")
        return v


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @validator("new_password")
    def validate_new_password(cls, v):
        if not any(c.islower() for c in v):
            raise ValueError("password must contain at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("password must contain at least one digit")
        if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in v):
            raise ValueError("password must contain at least one special character")
        return v


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_approved: bool
    profile_pic: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_pic: Optional[str] = None


# ─── Doctor Schemas ────────────────────────────────────────────────────────────

class DoctorBase(BaseModel):
    department: str
    mobile: Optional[str] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = 0
    consultation_fee: Optional[Decimal] = Decimal("0")
    bio: Optional[str] = None
    available_days: Optional[str] = "Mon,Tue,Wed,Thu,Fri"
    default_duration_minutes: Optional[int] = Field(30, ge=5, le=240)


class DoctorCreate(BaseModel):
    user: UserCreate
    doctor: DoctorBase


class DoctorResponse(DoctorBase):
    id: int
    user_id: int
    user: UserResponse
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorUpdate(DoctorBase):
    pass


# ─── Patient Schemas ───────────────────────────────────────────────────────────

class PatientBase(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=20)
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    blood_group: Optional[str] = None
    symptoms: Optional[str] = None
    medical_history: Optional[str] = None
    assigned_doctor_id: Optional[int] = None


class PatientCreate(BaseModel):
    user: UserCreate
    patient: PatientBase


class PatientResponse(PatientBase):
    id: int
    user_id: int
    user: UserResponse
    is_admitted: bool
    admit_date: Optional[date] = None
    discharge_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PatientUpdate(PatientBase):
    pass


# ─── Appointment Schemas ───────────────────────────────────────────────────────

class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_date: date
    appointment_time: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=240)
    description: Optional[str] = None

    @validator("appointment_time")
    def validate_time(cls, v):
        if v is None:
            return v
        try:
            from datetime import datetime as _dt
            _dt.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError(
                "appointment_time must be in HH:MM (24h) format"
            ) from None
        return v


class AppointmentCreate(AppointmentBase):
    patient_id: int


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: Optional[str] = None
    duration_minutes: Optional[int] = 30
    description: Optional[str] = None
    status: AppointmentStatus
    notes: Optional[str] = None
    patient: PatientResponse
    doctor: DoctorResponse
    created_at: datetime

    class Config:
        from_attributes = True


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=240)

    @validator("appointment_time")
    def validate_time(cls, v):
        if v is None:
            return v
        try:
            from datetime import datetime as _dt
            _dt.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError(
                "appointment_time must be in HH:MM (24h) format"
            ) from None
        return v


# ─── Discharge Schemas ─────────────────────────────────────────────────────────

class DischargeCreate(BaseModel):
    patient_id: int
    admit_date: date
    release_date: date
    room_charge: Decimal = Decimal("0")
    medicine_cost: Decimal = Decimal("0")
    doctor_fee: Decimal = Decimal("0")
    other_charges: Decimal = Decimal("0")
    diagnosis: Optional[str] = None
    treatment_summary: Optional[str] = None


class DischargeResponse(DischargeCreate):
    id: int
    days_spent: int
    total: Decimal
    created_at: datetime
    patient: PatientResponse

    class Config:
        from_attributes = True


# ─── Dashboard Schemas ─────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_doctors: int
    total_patients: int
    total_appointments: int
    pending_appointments: int
    admitted_patients: int
    todays_appointments: int
    revenue_this_month: Decimal
    approved_doctors: int
