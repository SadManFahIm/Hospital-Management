"""Doctor Service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Doctor, User
from app.schemas import DoctorCreate, DoctorUpdate
from app.core.security import get_password_hash


class DoctorService:
    @staticmethod
    async def get_doctors(db, skip=0, limit=20, department=None, is_approved=None):
        query = select(Doctor)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_doctor_by_id(db, doctor_id: int):
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_doctor(db, doctor_data: DoctorCreate):
        user = User(
            email=doctor_data.user.email,
            username=doctor_data.user.username,
            hashed_password=get_password_hash(doctor_data.user.password),
            first_name=doctor_data.user.first_name,
            last_name=doctor_data.user.last_name,
            role="doctor",
        )
        db.add(user)
        await db.flush()
        doctor = Doctor(user_id=user.id, **doctor_data.doctor.model_dump())
        db.add(doctor)
        await db.commit()
        await db.refresh(doctor)
        return doctor

    @staticmethod
    async def approve_doctor(db, doctor_id: int):
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        doctor = result.scalar_one_or_none()
        if doctor:
            user_result = await db.execute(select(User).where(User.id == doctor.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user.is_approved = True
            await db.commit()
            await db.refresh(doctor)
        return doctor

    @staticmethod
    async def update_doctor(db, doctor_id: int, data: DoctorUpdate):
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        doctor = result.scalar_one_or_none()
        if doctor:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(doctor, key, value)
            await db.commit()
            await db.refresh(doctor)
        return doctor

    @staticmethod
    async def delete_doctor(db, doctor_id: int):
        result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
        doctor = result.scalar_one_or_none()
        if doctor:
            await db.delete(doctor)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_doctor_patients(db, doctor_id: int):
        from app.models import Patient
        result = await db.execute(select(Patient).where(Patient.assigned_doctor_id == doctor_id))
        return result.scalars().all()
