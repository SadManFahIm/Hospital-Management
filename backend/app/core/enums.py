"""
Centralized Enum Definitions
Single source of truth for all application enums.
"""

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class AuditAction(str, enum.Enum):
    PATIENT_CREATED = "patient.created"
    PATIENT_UPDATED = "patient.updated"
    PATIENT_ADMITTED = "patient.admitted"
    PATIENT_DISCHARGED = "patient.discharged"
    PATIENT_DELETED = "patient.deleted"
    DOCTOR_CREATED = "doctor.created"
    DOCTOR_UPDATED = "doctor.updated"
    DOCTOR_APPROVED = "doctor.approved"
    DOCTOR_DELETED = "doctor.deleted"
    APPOINTMENT_CREATED = "appointment.created"
    APPOINTMENT_STATUS_CHANGED = "appointment.status_changed"
    APPOINTMENT_DELETED = "appointment.deleted"


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

    @classmethod
    def values(cls):
        return [e.value for e in cls]
