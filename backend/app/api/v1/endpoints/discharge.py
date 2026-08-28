"""Discharge endpoint"""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import require_admin
from app.models import DischargeDetails, Patient
from app.schemas import DischargeResponse

router = APIRouter()


@router.get("/", response_model=List[DischargeResponse])
async def list_discharges(db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)):
    from sqlalchemy import select

    result = await db.execute(
        select(DischargeDetails)
        .options(selectinload(DischargeDetails.patient).selectinload(Patient.user))
    )
    return result.scalars().all()
