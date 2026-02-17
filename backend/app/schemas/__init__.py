"""
Pydantic Schemas for Request/Response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


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
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.PATIENT


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
    consultation_fee: Optional[Decimal] = 0
    bio: Optional[str] = None
    available_days: Optional[str] = "Mon,Tue,Wed,Thu,Fri"


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
    description: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    patient_id: int


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: Optional[str] = None
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


# ─── Discharge Schemas ─────────────────────────────────────────────────────────

class DischargeCreate(BaseModel):
    patient_id: int
    admit_date: date
    release_date: date
    room_charge: Decimal = 0
    medicine_cost: Decimal = 0
    doctor_fee: Decimal = 0
    other_charges: Decimal = 0
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


class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    per_page: int
    pages: int
