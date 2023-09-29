from datetime import datetime
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_dialog import DialogRegistry, DialogManager, Window, Dialog
from aiogram_dialog.widgets.kbd import Next, Button, Cancel
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.input import MessageInput

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode


bot = Bot(token='6325210305:AAGZSFpDyFn2bfuH8jujhs6I_Ms5Pa9ZwTo')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

registry = DialogRegistry(dp)

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
    try:
        connection = sqlite3.connect('/home/intensa/database_dir/tulaevents.db')

        sql_query = """
            INSERT INTO events (event_name, description, age_restrictions, company, category, 
                                start_date, end_date, address, need_pre_reg, is_registered)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, False)
        """

        connection.execute(sql_query, event_arr)
        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        print(e)


async def on_input(m: types.Message, dialog: Dialog, manager: DialogManager):
    current_state = manager.current_context().state
    user_data = manager.current_context().dialog_data
    if current_state == EventRegistrationForm.event_name:
        user_data["event_name"] = m.text
    elif current_state == EventRegistrationForm.description:
        user_data["description"] = m.text
    elif current_state == EventRegistrationForm.age_restrictions:
        user_data["age_restrictions"] = m.text
    elif current_state == EventRegistrationForm.company:
        user_data["company"] = m.text
    elif current_state == EventRegistrationForm.category:
        user_data["category"] = m.text
    elif current_state == EventRegistrationForm.start_date:
        try:
            date_time = datetime.strptime(m.text, '%d-%m-%Y %H:%M').isoformat()
        except ValueError:
            date_time = datetime(2222, 12, 22, 22, 22).isoformat()
        user_data["start_date"] = date_time
    elif current_state == EventRegistrationForm.end_date:
        try:
            date_time = datetime.strptime(m.text, '%d-%m-%Y %H:%M').isoformat()
        except ValueError:
            date_time = datetime(2222, 12, 22, 22, 22).isoformat()
        user_data["end_date"] = date_time
    elif current_state == EventRegistrationForm.address:
        user_data["address"] = m.text
    await dialog.next()


async def on_date(m: types.Message, dialog: Dialog, manager: DialogManager):

    await dialog.next()


async def final_input(m: types.Message, dialog: Dialog, manager: DialogManager):
    m_text_lower = m.text.lower()
    need_pre_reg = 1 if m_text_lower == "да" else 0

    event_arr = [
        manager.current_context().dialog_data.get("event_name", ""),
        manager.current_context().dialog_data.get("description", ""),
        manager.current_context().dialog_data.get("age_restrictions", ""),
        manager.current_context().dialog_data.get("company", ""),
        manager.current_context().dialog_data.get("category", ""),
        manager.current_context().dialog_data.get("start_date", ""),
        manager.current_context().dialog_data.get("end_date", ""),
        manager.current_context().dialog_data.get("address", ""),
        need_pre_reg,
    ]

    await insert_event(event_arr)
    await manager.done()
    await reg_new(m)


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
        MessageInput(on_input),
        state=EventRegistrationForm.start_date,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Время окончания мероприятия в формате DD-MM-YYYY HH:MM"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
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

kb = [[
    types.KeyboardButton(text="Создать новое мероприятие"),
],
]


@dp.message_handler(Text(equals="Создать новое мероприятие"))
async def create_new_event(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(EventRegistrationForm.start, mode=StartMode.RESET_STACK)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb, one_time_keyboard=True)
    await message.answer("Привет! Для добавления нового мероприятия нажми на кнопку.",
                         reply_markup=keyboard)


async def reg_new(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb, one_time_keyboard=True)
    await message.answer("Регистрация окончена! Мероприятие успешно отправлено на модерацию!", reply_markup=keyboard)


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
