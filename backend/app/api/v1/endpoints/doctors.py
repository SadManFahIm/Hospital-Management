"""
Doctors API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import require_admin, require_doctor, get_current_user
from app.schemas import DoctorResponse, DoctorCreate, DoctorUpdate
from app.services.doctor_service import DoctorService

router = APIRouter()


@router.get("/", response_model=List[DoctorResponse])
async def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    department: Optional[str] = None,
    is_approved: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all doctors with optional filters"""
    doctors = await DoctorService.get_doctors(
        db, skip=skip, limit=limit, department=department, is_approved=is_approved
    )
    return doctors


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific doctor by ID"""
    doctor = await DoctorService.get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.post("/", response_model=DoctorResponse, status_code=201)
async def create_doctor(
    doctor_data: DoctorCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Create a new doctor (Admin only)"""
    return await DoctorService.create_doctor(db, doctor_data)


@router.put("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update doctor information"""
    # Doctors can update their own profile, admins can update any
    doctor = await DoctorService.get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if current_user.role != "admin" and doctor.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return await DoctorService.update_doctor(db, doctor_id, doctor_data)


@router.patch("/{doctor_id}/approve", response_model=DoctorResponse)
async def approve_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Approve a doctor (Admin only)"""
    doctor = await DoctorService.approve_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.delete("/{doctor_id}", status_code=204)
async def delete_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Delete a doctor (Admin only)"""
    success = await DoctorService.delete_doctor(db, doctor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found")


@router.get("/{doctor_id}/patients", response_model=List)
async def get_doctor_patients(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_doctor),
):
    """Get all patients assigned to a doctor"""
    return await DoctorService.get_doctor_patients(db, doctor_id)
