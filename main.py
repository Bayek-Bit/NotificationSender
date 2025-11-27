import asyncio
import logging
from datetime import datetime, timedelta, timezone

from database import create_tables, get_notifications_to_send, mark_notification_as_sent, schedule_notification
from models import Notification


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


class Scheduler:
    async def schedule(self, notification: Notification) -> None:
        """Планирует отправку уведомления"""
        db_id = await schedule_notification(notification)
        logging.info(f"Уведомление сохранено в БД с id={db_id}")

    async def _send(self, notification_row: dict) -> None:
        """Отправляет уведомление и помечает как отправленное"""
        logging.info(
            f">>> ОТПРАВКА: '{notification_row['message']}' "
            f"пользователю {notification_row['user_id']}"
        )

        # Здесь будет реальная отправка (Telegram, email и т.д.)
        # await send_to_user(notification_row["user_id"], notification_row["message"])

        await mark_notification_as_sent(notification_row)

    async def serve(self) -> None:
        """Основной цикл проверки и отправки уведомлений"""
        logging.info("Запуск планировщика уведомлений...")
        while True:
            pending = await get_notifications_to_send()

            if pending:
                for row in pending:
                    try:
                        await self._send(row)
                    except Exception as exc:  # noqa: BLE001
                        logging.error(f"Ошибка при отправке уведомления id={row['id']}: {exc}")

            await asyncio.sleep(5)


async def main() -> None:
    await create_tables()
    logging.info("Таблицы созданы")

    scheduler = Scheduler()

    # Пример добавления уведомлений (раскомментируй для теста)
    now = datetime.now(timezone.utc)
    await scheduler.schedule(Notification(user_id=1, message="Привет из async!", send_at=now + timedelta(seconds=5)))
    await scheduler.schedule(Notification(user_id=2, message="Второе уведомление через 12 сек", send_at=now + timedelta(seconds=12)))

    # Запускаем бесконечный цикл отправки
    await scheduler.serve()


if __name__ == "__main__":
    asyncio.run(main())