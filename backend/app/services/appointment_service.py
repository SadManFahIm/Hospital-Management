"""Appointment Service"""
from sqlalchemy import select

from app.models import Appointment
from app.schemas import AppointmentCreate, AppointmentUpdate


class AppointmentService:
    @staticmethod
    async def get_appointments(db, current_user, skip=0, limit=20, status=None,
                                doctor_id=None, patient_id=None, date_from=None, date_to=None):
        query = select(Appointment)
        if status:
            query = query.where(Appointment.status == status)
        if doctor_id:
            query = query.where(Appointment.doctor_id == doctor_id)
        if patient_id:
            query = query.where(Appointment.patient_id == patient_id)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_appointment_by_id(db, appointment_id: int):
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_appointment(db, data: AppointmentCreate):
        appt = Appointment(**data.model_dump())
        db.add(appt)
        await db.commit()
        await db.refresh(appt)
        return appt

    @staticmethod
    async def update_appointment(db, appointment_id: int, data: AppointmentUpdate):
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        appt = result.scalar_one_or_none()
        if appt:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(appt, key, value)
            await db.commit()
            await db.refresh(appt)
        return appt

    @staticmethod
    async def delete_appointment(db, appointment_id: int):
        result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
        appt = result.scalar_one_or_none()
        if appt:
            await db.delete(appt)
            await db.commit()
            return True
        return False
