import asyncio
from dataclasses import dataclass
from datetime import datetime as dt

from database import schedule_notification

@dataclass
class Notification:
        user_id: int
        message: str
        time_to_notify: dt


class Scheduler:
    def __init__(self):
        self.__notification_list = []

    def schedule(self, notification: Notification):
        self.__notification_list.append(notification)

        try:
            asyncio.run(
                self._save_to_db(notification)
            )
        except Exception as ex:
            print(ex)

    async def _save_to_db(self, notification: Notification):
        db_id = await schedule_notification(
            user_id=int(notification.user_id),
            message=notification.message,
            send_at=notification.time_to_notify,
        )
        print(f"Сохранено в БД с id={db_id}")

    def run_pending(self):
        pass


scheduler = Scheduler()
scheduler.schedule(Notification("Hbm-12", "Вас привестствует программа бета-теста.", dt.now()))
scheduler.run_pending()  # Отправляем сообщение, так как небольшое время прошло)

scheduler.schedule(Notification("abc-4F", "Вы в 2050!", dt(year=2050, month=1, day=1)))
# Ничего не выведет, ибо старое уведомление отправлено и удалено из списка
# А 2050 еще не наступил)
scheduler.run_pending()


def check_age(age: int):
    if isinstance(age, int):
        if age < 18:
            raise ValueError("Вы должны быть старше 18 лет")
    else:
        raise TypeError("Введите корректное число")


class TaskError(Exception):
    def __init__(self, message):
        super().__init__(message)


class TaskManager:
    def __init__(self):
        self.__task_list = []

    def add_task(self, task: dict):
        if isinstance(task, dict):
            title = task.get("title")
            completed = task.get("completed")

            if (title is None) or (completed is None):
                raise TaskError("Задание должно содержать ключи title и completed")
        else:
            raise TypeError("Неверный тип данных. Задание необходимо передавать в словаре(dict)")


task_manager = TaskManager()
# Так как мы не обрабатываем исключение, то программа завершится на следующей строчке
task_manager.add_task({"title": "Купить шкаф"})  # -> TaskError; кастомное исключение
# И для собственного желания еще один кейс, который завершит нашу программу
# Хоть она и завершилась уже на прошлом исключении
task_manager.add_task(["Купить кухню"])  # -> TypeError; неверный тип данных
