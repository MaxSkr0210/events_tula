from datetime import datetime
import os
import sqlite3

import aiogram_dialog.widgets.input.base
from aiogram import Bot, Dispatcher, executor

from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next, Button, Cancel
from aiogram_dialog.widgets.text import Const

storage = MemoryStorage()
bot = Bot(token='6325210305:AAGZSFpDyFn2bfuH8jujhs6I_Ms5Pa9ZwTo')
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)

event_array = []


class EventRegistrationForm(StatesGroup):
    start = State()
    event_name = State()
    description = State()
    age_restrictions = State()
    company = State()
    category = State()
    start_date = State()
    end_date = State()
    address = State()
    need_pre_reg = State()


async def insert_event(event_arr):
    global event_array
    connection = sqlite3.connect('/home/intensa/database_dir/tulaevents.db')
    try:
        sql_query = """
            INSERT INTO events (event_name, description, age_restrictions, company, category, 
                                start_date, end_date, address, need_pre_reg, is_registered)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, False)
        """

        connection.execute(sql_query, event_arr)

        event_array = []

        connection.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        connection.close()


async def on_input(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    event_array.append(m.text)
    await dialog.next()


async def on_date(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    date_time = datetime.strptime(m.text, '%d-%m-%Y %H:%M').isoformat()
    event_array.append(date_time)
    await dialog.next()


async def final_input(m: Message, dialog: Dialog, manager: DialogManager):
    m_text_lower = m.text.lower()
    event_array.append(1 if m_text_lower == "да" else 0 if m_text_lower == "нет" else 0)
    await insert_event(event_array)
    await m.answer("Регистрация окончена! Мероприятие успешно отправлено на модерацию!")
    await dialog.switch_to(state=EventRegistrationForm.start)


async def go_back(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().back()


async def go_next(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().next()


dialog = Dialog(
    Window(
        Const("Для начала регистрации нажмите \"Начать\""),
        Button(Const("Начать"), id="next", on_click=go_next),
        state=EventRegistrationForm.start,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Название мероприятия"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.event_name,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Описание мероприятия"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.description,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Возрастные ограничения"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.age_restrictions,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Название Вашей компании"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.company,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Категория (Формат)"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.category,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Время начала мероприятия в формате DD-MM-YYYY HH:MM"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_date),
        state=EventRegistrationForm.start_date,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Время окончания мероприятия в формате DD-MM-YYYY HH:MM"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_date),
        state=EventRegistrationForm.end_date,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Адрес проведения мероприятия"),
        Button(Const("Назад"), id="backTime", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.address,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Требуется ли предварительная запись участников?(Да/Нет)"),
        Button(Const("Назад"), id="backPay", on_click=go_back),
        MessageInput(final_input),
        state=EventRegistrationForm.need_pre_reg,
        preview_add_transitions=[Cancel()]
    ),
)

registry.register(dialog)


@dp.message_handler(commands=["start"])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(EventRegistrationForm.start, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
