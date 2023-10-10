import sqlite3
from datetime import datetime, timedelta


def connection_decorator(func):
    def wrapper(*args, **kwargs):
        # connection = sqlite3.connect('/home/intensa/database_dir/tulaevents.db')
        connection = sqlite3.connect('tulaevents.db')
        result = func(connection, *args, **kwargs)
        connection.commit()
        connection.close()
        return result

    return wrapper


@connection_decorator
def get_event_by_page_number(connection, id):
    page_number = id
    cursor = connection.execute("SELECT * FROM events")
    try:
        event_array = list(cursor)[page_number - 1]
        event_name = event_array[1]
        event_description = event_array[2]
        event_age_restrictions = event_array[3]
        event_company = event_array[4]
        datetime_obj = datetime.fromisoformat(event_array[6])
        event_datetime = datetime_obj.strftime("%d-%m-%Y %H:%M")
        event_location = event_array[8]
        event_pre_reg = bool(event_array[10])

        formatted_string = f"*{event_name} {event_age_restrictions}*\nНачало: {event_datetime}\n\nОписание: {event_description}\n\n{'Требуется предварительная регистрация!' if event_pre_reg else 'Предварительная регистрация не требуется!'}\n\nАдрес: {event_location}\n\n\"{event_company}\""

        return formatted_string
    except IndexError:
        return "None"


@connection_decorator
def get_event_object_by_page_number(connection, id):
    page_number = id
    cursor = connection.execute("SELECT * FROM events")
    try:
        return list(cursor)[page_number - 1]
    except IndexError:
        return "None"


@connection_decorator
def print_all(connection):
    cursor = connection.execute("SELECT * FROM events")
    lst = list(cursor)
    return lst


@connection_decorator
def check_user_registration(connection, chat_id, event_id):
    cursor = connection.execute("SELECT * FROM users WHERE chat_id = ? AND event_id = ?", (chat_id, event_id))
    data = cursor.fetchall()
    if len(data) == 0:
        return False, False
    else:
        is_registered = data[0][3]
        if is_registered:
            return True, True
        else:
            return True, False


@connection_decorator
def create_record(connection, chat_id, event_id):
    connection.execute("INSERT INTO users (chat_id, event_id, is_registered) VALUES (?, ?, false)", (chat_id, event_id))


@connection_decorator
def register_user(connection, chat_id, event_id):
    connection.execute("UPDATE users SET is_registered = true WHERE chat_id = ? AND event_id = ?", (chat_id, event_id))


@connection_decorator
def unregister_user(connection, chat_id, event_id):
    connection.execute("UPDATE users SET is_registered = false WHERE chat_id = ? AND event_id = ?", (chat_id, event_id))


@connection_decorator
def get_events_count(connection):
    cursor = connection.execute("SELECT COUNT(*) FROM events")
    data = cursor.fetchall()
    return data[0][0]


@connection_decorator
def create_reminder_in_db(connection, event_id, chat_id, remind_time):
    connection.row_factory = sqlite3.Row
    cursor = connection.execute("SELECT * FROM reminders")
    result = []
    for r in cursor.fetchall():
        result.append((dict(r)))
    user_id = chat_id
    try:
        if (user_id, str(remind_time)) in [(result[i]['user_id'], result[i]['reminder_time']) for i in range(len(result))]:
            return True
        else:
            connection.execute("INSERT INTO reminders (event_id, user_id, reminder_time) VALUES (?, ?, ?)",
                               (event_id, chat_id, remind_time))
            return False
    finally:
        pass


@connection_decorator
def checker(connection):
    # Получаем текущее время
    now = datetime.now()
    # Выполняем запрос на выборку пользователей с временем напоминания меньше текущего времени
    cursor = connection.execute("SELECT user_id, reminder_time FROM reminders WHERE reminder_time < ?", (now,))

    # Обрабатываем каждую запись результата запроса
    for row in cursor:
        user_id = row[0]
        reminder_time = row[1]
        connection.execute("DELETE FROM reminders WHERE user_id = ? AND reminder_time < ?", (user_id, now,))
        return user_id

    return None
