from datetime import datetime as dt


class Notification:
    def __init__(self, user_id: str, message: str, time_to_notify: dt):
        self.user_id = user_id
        self.message = message
        self.time_to_notify = time_to_notify


class Scheduler:
    def __init__(self):
        self.__notification_list = []

    def schedule(self, notification: Notification):
        self.__notification_list.append(notification)

    def run_pending(self):
        for notification in self.__notification_list:
            date_now = dt.now()
            if date_now > notification.time_to_notify:
                # Форматируем уведомление, которое будет отправлено
                # Потом добавлю либо полноценные логи, либо просто сообщение будет на английском языке
                print(f"Сообщение для пользователя {notification.user_id} отправлено.\
                    \nТекст сообщения: {notification.message}\
                    \nЗапланированное время: {notification.time_to_notify}\
                    \nДата фактического отправления: {date_now}\
                ")
                # Удаляем уведомление, ибо мы его уже отправили
                self.__notification_list.remove(notification)


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
