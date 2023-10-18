import hashlib
import os
import requests
from datetime import datetime
import sqlite3

import aiogram_dialog.widgets.media
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, ContentType
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.types import InputFile

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_dialog import DialogRegistry, DialogManager, Window, Dialog, ShowMode
from aiogram_dialog.widgets.kbd import Next, Button, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.input import MessageInput

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode


bot = Bot(token='6325210305:AAGZSFpDyFn2bfuH8jujhs6I_Ms5Pa9ZwTo')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

registry = DialogRegistry(dp)

IMG_SAVE_PATH = "/home/intensa/static/uploads/"


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
    img_link = State()
    img_failed = State()
    need_pre_reg = State()
    final_input = State()
    approve_input = State()


async def insert_event(event_arr):
    try:
        connection = sqlite3.connect('/home/intensa/database_dir/tulaevents.db')
        sql_query = """
            INSERT INTO events (event_name, description, age_restrictions, company, category, 
                                start_date, end_date, address, img_link, need_pre_reg, is_registered)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, False)
        """

        connection.execute(sql_query, event_arr)
        connection.commit()
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


async def on_image(m: types.Message, dialog: Dialog, manager: DialogManager):
    user_data = manager.current_context().dialog_data
    random_hash = hashlib.sha256(os.urandom(24)).hexdigest()
    unique_filename = f"{random_hash}.jpg"
    try:
        if m.content_type == "text":
            response = requests.get(m.text)
            if response.status_code == 200:
                with open(IMG_SAVE_PATH + unique_filename, "wb") as file:
                    file.write(response.content)
        img_link = ""
        if m.content_type == "document":
            doc_id = m.document.file_id
            file = await bot.download_file_by_id(file_id=doc_id)
            with open(IMG_SAVE_PATH + unique_filename, 'wb') as f:
                f.write(file.getvalue())
        if m.content_type == "photo":
            file_id = m.photo[-1].file_id
            user_data['img_preview'] = file_id
            file = await bot.download_file_by_id(file_id=file_id)
            with open(IMG_SAVE_PATH + unique_filename, 'wb') as f:
                f.write(file.getvalue())
        user_data['img_link'] = unique_filename
        await dialog.switch_to(EventRegistrationForm.need_pre_reg)
    except Exception as e:
        await dialog.switch_to(EventRegistrationForm.img_failed)


async def final_input(c: CallbackQuery, button: Button, manager: DialogManager):
    manager.show_mode = ShowMode.SEND
    user_data = manager.current_context().dialog_data
    m_text_lower = button.widget_id.lower()
    user_data["need_pre_reg"] = 1 if m_text_lower == "agreeprereg" else 0
    event_arr = [
        manager.current_context().dialog_data.get("event_name", ""),
        manager.current_context().dialog_data.get("description", ""),
        manager.current_context().dialog_data.get("age_restrictions", ""),
        manager.current_context().dialog_data.get("company", ""),
        manager.current_context().dialog_data.get("category", ""),
        manager.current_context().dialog_data.get("start_date", ""),
        manager.current_context().dialog_data.get("end_date", ""),
        manager.current_context().dialog_data.get("address", ""),
        manager.current_context().dialog_data.get("img_link", ""),
        manager.current_context().dialog_data.get("need_pre_reg", ""),
    ]
    event_name = event_arr[0]
    event_description = event_arr[1]
    event_age_restrictions = event_arr[2]
    event_company = event_arr[3]
    datetime_obj = datetime.fromisoformat(event_arr[5])
    event_datetime = datetime_obj.strftime("%d-%m-%Y %H:%M")
    event_location = event_arr[7]
    event_img_link = event_arr[8]
    event_pre_reg = bool(event_arr[9])
    formatted_string = f"{event_name} {event_age_restrictions}*\nНачало: {event_datetime}\n\nОписание: {event_description}\n\n{'Требуется предварительная регистрация!' if event_pre_reg else 'Предварительная регистрация не требуется!'}\n\nАдрес: {event_location}\n\n\"{event_company}\""
    user_data['event_arr'] = event_arr

    event_img_preview = manager.current_context().dialog_data.get("img_preview", "")
    if event_img_preview != "":
        await c.message.answer_photo(photo=event_img_preview, caption=formatted_string)
        await manager.switch_to(EventRegistrationForm.approve_input)
    elif event_img_link != "":
        event_img_link = IMG_SAVE_PATH + event_img_link
        await c.message.answer_photo(photo=InputFile(event_img_link), caption=formatted_string)
        await manager.switch_to(EventRegistrationForm.approve_input)
    else:
        await c.message.answer(formatted_string)

    await manager.switch_to(EventRegistrationForm.approve_input)


async def agree_input(c: CallbackQuery, button: Button, manager: DialogManager):
    event_arr = manager.current_context().dialog_data.get("event_arr", ""),
    event = event_arr[0]
    await insert_event(event)
    await manager.done()
    await reg_new(c.message)


async def go_back(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().back()


async def go_next(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().next()


dialog = Dialog(
    Window(
        Const("Введите название мероприятия"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.event_name,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Введите описание для мероприятия"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.description,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Введите возрастные ограничения ( если их нет, укажите “0+” )"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.age_restrictions,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Введите название вашей компании"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.company,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Опишите формат мероприятия, например “Рукоделие”"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.category,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Введите время старта мероприятия в формате ДД-ММ-ГГГГ ЧЧ:ММ"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.start_date,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Введите время окончания мероприятия в формате ДД-ММ-ГГГГ ЧЧ:ММ"),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.end_date,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Введите адрес проведения мероприятия"),
        Button(Const("Назад"), id="backTime", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.address,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Приложите фотографию для мероприятия или продолжите без неё"),
        SwitchTo(Const("Продолжить без фото"), id="continueWithoutPhoto", state=EventRegistrationForm.need_pre_reg),
        Button(Const("Назад"), id="backStart", on_click=go_back),
        MessageInput(on_image, content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT]),
        state=EventRegistrationForm.img_link,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Ошибка при загрузке фото, повторите попытку!"),
        Button(Const("Продолжить без фото"), id="nextWithoutPhoto", on_click=go_next),
        SwitchTo(Const("Назад"), id="backToAdrs", state=EventRegistrationForm.address),
        MessageInput(on_image, content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT]),
        state=EventRegistrationForm.img_failed,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Участникам нужно записываться на мероприятие?"),
        Button(Const("Да"), id="agreePreReg", on_click=final_input),
        Button(Const("Нет"), id="disagreePreReg", on_click=final_input),
        SwitchTo(Const("Назад"), id="backToAdrs", state=EventRegistrationForm.address),
        state=EventRegistrationForm.need_pre_reg,
        preview_add_transitions=[Next()]
    ),
    Window(
        Const("Вся информация в карточке заполнена корректно?"),
        Button(Const("Да"), id="agreeInput", on_click=agree_input),
        SwitchTo(Const("Нет"), id="disagreeInput", state=EventRegistrationForm.event_name),
        state=EventRegistrationForm.approve_input,
        preview_add_transitions=[Cancel()],
    ),
)

registry.register(dialog)

kb = [[
    types.KeyboardButton(text="Создать новое мероприятие"),
],
]


@dp.message_handler(Text(equals="Создать новое мероприятие"))
async def create_new_event(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(EventRegistrationForm.event_name, mode=StartMode.RESET_STACK)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb, one_time_keyboard=True)
    await message.answer("Привет! Для создания мероприятия нажми на кнопку!",
                         reply_markup=keyboard)


async def reg_new(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kb, one_time_keyboard=True)
    await message.answer("Создание мероприятия завершено. Ваше мероприятие отправлено на модерацию, после прохождения модерации мероприятие будет опубликовано.", reply_markup=keyboard)


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
