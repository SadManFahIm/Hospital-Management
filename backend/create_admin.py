import asyncio

from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models import User, UserRole


async def create_admin():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        admin = User(
            email="admin@medcore.com",
            username="admin",
            hashed_password=get_password_hash("Admin@1234"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
            is_approved=True
        )
        db.add(admin)
        await db.commit()
        print("✅ Admin user created successfully!")

asyncio.run(create_admin())
