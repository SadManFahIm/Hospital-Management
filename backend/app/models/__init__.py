"""
SQLAlchemy Database Models
"""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.enums import AppointmentStatus, AuditAction, Department, UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    profile_pic = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    patient_profile = relationship("Patient", back_populates="user", uselist=False)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    department = Column(SAEnum(Department), nullable=False)
    mobile = Column(String(20), nullable=True)
    address = Column(String(200), nullable=True)
    qualification = Column(String(200), nullable=True)
    experience_years = Column(Integer, default=0)
    consultation_fee = Column(Numeric(10, 2), default=0)
    bio = Column(Text, nullable=True)
    available_days = Column(String(200), default="Mon,Tue,Wed,Thu,Fri")
    default_duration_minutes = Column(Integer, default=30)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor")
    patients = relationship("Patient", back_populates="assigned_doctor")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    assigned_doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    mobile = Column(String(20), nullable=False)
    address = Column(String(200), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    blood_group = Column(String(10), nullable=True)
    symptoms = Column(String(500), nullable=True)
    medical_history = Column(Text, nullable=True)
    admit_date = Column(Date, nullable=True)
    discharge_date = Column(Date, nullable=True)
    is_admitted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="patient_profile")
    assigned_doctor = relationship("Doctor", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")
    discharge_details = relationship("DischargeDetails", back_populates="patient", uselist=False)


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        # Support the most common query patterns: scheduling lookups by doctor
        # or patient on a given date, and status filtering.
        Index("ix_appointments_doctor_date", "doctor_id", "appointment_date"),
        Index("ix_appointments_patient_date", "patient_id", "appointment_date"),
        Index("ix_appointments_status", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(Date, nullable=False, index=True)
    appointment_time = Column(String(20), nullable=True)
    duration_minutes = Column(Integer, default=30)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(AppointmentStatus), default=AppointmentStatus.PENDING)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")


class DischargeDetails(Base):
    __tablename__ = "discharge_details"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), unique=True, nullable=False)
    admit_date = Column(Date, nullable=False)
    release_date = Column(Date, nullable=False)
    days_spent = Column(Integer, nullable=False)
    room_charge = Column(Numeric(10, 2), default=0)
    medicine_cost = Column(Numeric(10, 2), default=0)
    doctor_fee = Column(Numeric(10, 2), default=0)
    other_charges = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    diagnosis = Column(Text, nullable=True)
    treatment_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="discharge_details")


class TokenBlacklist(Base):
    """Blacklisted (revoked) JWT tokens (revoked access tokens), e.g. after logout."""
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(255), unique=True, index=True, nullable=False)
    token_type = Column(String(20), nullable=False, default="access")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RefreshSession(Base):
    """Tracks issued refresh tokens per user. Enables rotation reuse detection,
    per-user session revocation (logout), and revoke-all on password change."""
    __tablename__ = "refresh_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    jti = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", backref="refresh_sessions")


class AuditLog(Base):
    """Immutable trace of significant actions (see docs/DOMAIN_MODEL.md).

    Never stores passwords, tokens, or unnecessary medical payloads.
    ``actor_user_id`` is nullable (system/background actions); no cascade so a
    deleted user does not destroy the audit trail.
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_created_at", "created_at"),
        Index("ix_audit_logs_actor", "actor_user_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor_role = Column(String(20), nullable=True)
    action = Column(SAEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    request_id = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    actor = relationship("User", foreign_keys=[actor_user_id])
