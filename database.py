import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models import Base
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def schedule_notification(user_id: int,
                                message: str,
                                send_at: datetime
                            ) -> bool:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            pass


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Запуск
asyncio.run(create_tables())