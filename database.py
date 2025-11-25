import asyncio
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models import Base
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def schedule_notification(
        user_id: int,
        message: str,
        send_at: datetime
    ) -> int | None:

    if send_at.tzinfo is None:
        send_at = send_at.replace(tzinfo=timezone.utc)

    if send_at <= datetime.now(timezone.utc):
        raise ValueError("Send time(send_at) should be in future")

    query = text("""
        INSERT INTO scheduled_notifications (user_id, message, send_at, status)
        VALUES (:user_id, :message, :send_at, 'pending')
        RETURNING id
    """)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                query,
                {
                    "user_id": user_id,
                    "message": message,
                    "send_at": send_at
                }
            )
            return result.scalar_one()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await schedule_notification(1, "Hello", datetime(2025, 11, 26))

# Запуск
asyncio.run(create_tables())