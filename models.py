from typing import List, Optional
from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Text


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    fullname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Связь один-ко-многим с уведомлениями
    notifications: Mapped[List["Notification"]] = relationship(
        "Notifications",
        back_populates="user",
        cascade="all, delete-orphan",  # если удаляем пользователя — удалятся его уведомления
        lazy="selectin",  # эффективная загрузка (рекомендуется для async)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Notification(Base):
    __tablename__ = "scheduled_notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Правильный ForeignKey с указанием колонки
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False, index=True
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)

    send_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pending",  # лучше на уровне БД
        default="pending",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Обратная связь к пользователю
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        lazy="joined",  # или "selectin" — зависит от сценария
    )

    def __repr__(self) -> str:
        return (
            f"Notification(id={self.id!r}, user_id={self.user_id!r}, "
            f"status={self.status!r}, send_at={self.send_at!r})"
        )
