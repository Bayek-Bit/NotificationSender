import asyncio
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models import Base, Notification
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def schedule_notification(notification: Notification) -> int | None:
    send_at = notification.send_at
    if send_at.tzinfo is None:
        send_at = notification.send_at.replace(tzinfo=timezone.utc)

    if notification.send_at <= datetime.now(timezone.utc):
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
                    "user_id": notification.user_id,
                    "message": notification.message,
                    "send_at": send_at
                }
            )
            return result.scalar_one()

async def get_notifications_to_send():
    """Get notifications to send from datetime now"""
    now = datetime.now(timezone.utc)
    # Пока не совсем атомарно)
    query = text("""
        SELECT * FROM scheduled_notifications
        WHERE send_at <= (:now)
        AND status = 'pending'
    """)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            query,
            {
                "now": now
            }
        )
        return result.mappings().all()

async def mark_notification_as_sent(notification: dict):
    query = text("""
        UPDATE scheduled_notifications
        SET status = 'sent'
        WHERE id = :notification_id AND user_id = :user_id
    """)

    async with AsyncSessionLocal() as session:
        try:
            await session.execute(
                query,
                {
                    "notification_id": notification['id'],
                    "user_id": notification['user_id']
                }
            )
            await session.commit()
            return True
        except Exception as ex:
            print(ex)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        a = await get_notifications_to_send()
        print(a)
