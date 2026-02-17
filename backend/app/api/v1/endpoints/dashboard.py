"""
Dashboard Analytics Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, datetime
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas import DashboardStats
from app.models import User, Doctor, Patient, Appointment, DischargeDetails

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Get comprehensive dashboard statistics (Admin only)"""
    today = date.today()
    first_of_month = today.replace(day=1)

    # Total counts
    total_doctors = await db.scalar(select(func.count(Doctor.id)))
    total_patients = await db.scalar(select(func.count(Patient.id)))
    total_appointments = await db.scalar(select(func.count(Appointment.id)))

    # Pending appointments
    pending_appointments = await db.scalar(
        select(func.count(Appointment.id)).where(Appointment.status == "pending")
    )

    # Admitted patients
    admitted_patients = await db.scalar(
        select(func.count(Patient.id)).where(Patient.is_admitted == True)
    )

    # Today's appointments
    todays_appointments = await db.scalar(
        select(func.count(Appointment.id)).where(Appointment.appointment_date == today)
    )

    # Revenue this month
    revenue_result = await db.scalar(
        select(func.sum(DischargeDetails.total)).where(
            DischargeDetails.created_at >= first_of_month
        )
    )
    revenue_this_month = Decimal(str(revenue_result or 0))

    # Approved doctors
    approved_doctors = await db.scalar(
        select(func.count(User.id)).where(
            and_(User.role == "doctor", User.is_approved == True)
        )
    )

    return DashboardStats(
        total_doctors=total_doctors or 0,
        total_patients=total_patients or 0,
        total_appointments=total_appointments or 0,
        pending_appointments=pending_appointments or 0,
        admitted_patients=admitted_patients or 0,
        todays_appointments=todays_appointments or 0,
        revenue_this_month=revenue_this_month,
        approved_doctors=approved_doctors or 0,
    )


@router.get("/doctor-stats")
async def get_doctor_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get stats for the logged-in doctor"""
    if current_user.role not in ["doctor", "admin"]:
        return {"error": "Access denied"}

    doctor = await db.scalar(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    if not doctor:
        return {}

    today = date.today()
    total_patients = await db.scalar(
        select(func.count(Patient.id)).where(Patient.assigned_doctor_id == doctor.id)
    )
    today_appointments = await db.scalar(
        select(func.count(Appointment.id)).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == today,
            )
        )
    )
    pending = await db.scalar(
        select(func.count(Appointment.id)).where(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.status == "pending",
            )
        )
    )

    return {
        "total_patients": total_patients or 0,
        "today_appointments": today_appointments or 0,
        "pending_appointments": pending or 0,
    }


@router.get("/patient-stats")
async def get_patient_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get stats for the logged-in patient"""
    patient = await db.scalar(
        select(Patient).where(Patient.user_id == current_user.id)
    )
    if not patient:
        return {}

    total_appointments = await db.scalar(
        select(func.count(Appointment.id)).where(Appointment.patient_id == patient.id)
    )
    pending = await db.scalar(
        select(func.count(Appointment.id)).where(
            and_(
                Appointment.patient_id == patient.id,
                Appointment.status == "pending",
            )
        )
    )

    return {
        "total_appointments": total_appointments or 0,
        "pending_appointments": pending or 0,
        "is_admitted": patient.is_admitted,
        "admit_date": str(patient.admit_date) if patient.is_admitted else None,
    }
