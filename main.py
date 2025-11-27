import asyncio

import logging

from database import schedule_notification, get_notifications_to_send, mark_notification_as_sent, create_tables
from models import Notification


class Scheduler:
    async def schedule(self, notification: Notification):
        await self._save_to_db(notification)

    async def _save_to_db(self, notification: Notification):
        db_id = await schedule_notification(notification)
        logging.info(f"[INFO] Сохранено в БД с id={db_id}")

    async def _send(self, notification):
        # Логика отправки
        logging.info(f">>> ОТПРАВКА: {notification['message']} пользователю {notification['user_id']}")

        await mark_notification_as_sent(notification)

    async def serve(self):
        # Получаем актуальное время
        # Находим записи, которые надо отправить
        # Отправляем
        # Меняем статус в бд
        # Удаляем из списка
        while True:
            pending_tasks = await get_notifications_to_send()
            # Если есть, что отправить
            if pending_tasks:
                for task in pending_tasks:
                    try:
                        await self._send(task)
                    except Exception as ex:
                        logging.warning(ex)

            await asyncio.sleep(5)


async def main():
    await create_tables()

    scheduler = Scheduler()
    await scheduler.serve()
    # TODO: метод для записи нового уведомления
    # await scheduler.schedule(Notification(1, "Привет из async!", dt.now() + timedelta(seconds=3)))
    # await scheduler.schedule(Notification(2, "Второе уведомление", dt.now() + timedelta(seconds=10)))

    await asyncio.sleep(15)  # даём поработать


if __name__ == "__main__":
    asyncio.run(main())
