"""
SQLAlchemy Database Models
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Text,
    ForeignKey, Enum as SAEnum, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Department(str, enum.Enum):
    CARDIOLOGIST = "Cardiologist"
    DERMATOLOGIST = "Dermatologist"
    EMERGENCY = "Emergency Medicine"
    ALLERGIST = "Allergist/Immunologist"
    ANESTHESIOLOGIST = "Anesthesiologist"
    SURGEON = "Colon and Rectal Surgeon"
    NEUROLOGIST = "Neurologist"
    ORTHOPEDIC = "Orthopedic Surgeon"
    PEDIATRICIAN = "Pediatrician"
    PSYCHIATRIST = "Psychiatrist"
    RADIOLOGIST = "Radiologist"
    ONCOLOGIST = "Oncologist"


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

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(String(20), nullable=True)
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
