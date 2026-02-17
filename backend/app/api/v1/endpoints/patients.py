"""Patients endpoint placeholder"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
router = APIRouter()

@router.get("/")
async def list_patients(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from sqlalchemy import select
    from app.models import Patient
    result = await db.execute(select(Patient).offset(skip).limit(limit))
    return result.scalars().all()

@router.patch("/{patient_id}/admit")
async def admit_patient(patient_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)):
    from sqlalchemy import select
    from app.models import Patient
    from datetime import date
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient.is_admitted = True
    patient.admit_date = date.today()
    await db.commit()
    return {"message": "Patient admitted successfully"}

@router.patch("/{patient_id}/discharge")  
async def discharge_patient(patient_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)):
    from sqlalchemy import select
    from app.models import Patient
    from datetime import date
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient.is_admitted = False
    patient.discharge_date = date.today()
    await db.commit()
    return {"message": "Patient discharged successfully"}
