from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import DATABASE_URL
from models import Base, Notification


# Создание engine и сессии
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def schedule_notification(notification: Notification) -> int:
    send_at = notification.send_at
    if send_at.tzinfo is None:
        send_at = send_at.replace(tzinfo=timezone.utc)

    if send_at <= datetime.now(timezone.utc):
        raise ValueError("send_at должен быть в будущем")

    query = text(
        """
        INSERT INTO scheduled_notifications (user_id, message, send_at, status)
        VALUES (:user_id, :message, :send_at, 'pending')
        RETURNING id
        """
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            query,
            {
                "user_id": notification.user_id,
                "message": notification.message,
                "send_at": send_at,
            },
        )
        new_id = result.scalar_one()
        await session.commit()
        return new_id


async def get_notifications_to_send() -> list[dict]:
    now = datetime.now(timezone.utc)

    query = text(
        """
        SELECT *
        FROM scheduled_notifications
        WHERE send_at <= :now AND status = 'pending'
        """
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(query, {"now": now})
        return result.mappings().all()


async def mark_notification_as_sent(notification_row: dict) -> None:
    query = text(
        """
        UPDATE scheduled_notifications
        SET status = 'sent'
        WHERE id = :notification_id AND user_id = :user_id
        """
    )

    async with AsyncSessionLocal() as session:
        await session.execute(
            query,
            {
                "notification_id": notification_row["id"],
                "user_id": notification_row["user_id"],
            },
        )
        await session.commit()


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)