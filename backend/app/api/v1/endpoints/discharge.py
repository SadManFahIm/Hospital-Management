"""Discharge endpoint"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user, require_admin
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
router = APIRouter()

@router.get("/")
async def list_discharges(db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)):
    from sqlalchemy import select
    from app.models import DischargeDetails
    result = await db.execute(select(DischargeDetails))
    return result.scalars().all()
