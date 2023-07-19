import asyncio
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import exceptions
from db import get_event_by_page_number, check_user_registration, register_user, unregister_user, create_record, create_reminder_in_db
from cfg import API_TOKEN


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.callback_query_handler(text_startswith="page_prev")
async def handle_prev_page(call: types.CallbackQuery):
    page_number = int(call.data.split(":")[1]) - 1
    await update_page_markup(call.message, call.from_user['id'], call.id, page_number)


@dp.callback_query_handler(text_startswith="page_next")
async def handle_next_page(call: types.CallbackQuery):
    page_number = int(call.data.split(":")[1]) + 1
    await update_page_markup(call.message, call.from_user['id'], call.id, page_number)


@dp.callback_query_handler(text_startswith="page_register")
async def handle_register_user(call: types.CallbackQuery):
    page_number = int(call.data.split(":")[1])
    register_user(call.from_user['id'], page_number)
    await update_page_markup(call.message, call.from_user['id'], call.id, page_number)


@dp.callback_query_handler(text_startswith="page_unregister")
async def handle_unregister_user(call: types.CallbackQuery):
    page_number = int(call.data.split(":")[1])
    unregister_user(call.from_user['id'], page_number)
    await update_page_markup(call.message, call.from_user['id'], call.id, page_number)


@dp.message_handler(commands=["start"])
async def handle_start_command(msg: types.Message):
    if_exists, is_registered = check_user_registration(chat_id=msg.from_id, event_id=1)
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Назад", callback_data=f"page_prev:0"),
        InlineKeyboardButton("1", callback_data="null"),
        InlineKeyboardButton("Вперёд", callback_data=f"page_next:1"),
    )

    if not if_exists:
        create_record(msg.from_id, 1)

    if is_registered:
        markup.row(InlineKeyboardButton("Анрег", callback_data=f"page_unregister:1"))
    else:
        markup.row(InlineKeyboardButton("Рег", callback_data=f"page_register:1"))
    markup.row(InlineKeyboardButton("Напомнить", callback_data="reminder:1"))
    await msg.answer(str(get_event_by_page_number(1)), reply_markup=markup)


async def update_page_markup(message, user_id, call_id, page_number):
    if_exists, is_registered = check_user_registration(chat_id=user_id, event_id=page_number)
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Назад", callback_data=f"page_prev:{page_number}"),
        InlineKeyboardButton(str(page_number), callback_data="null"),
        InlineKeyboardButton("Вперёд", callback_data=f"page_next:{page_number}")
    )

    if not if_exists:
        create_record(user_id, page_number)

    if is_registered:
        markup.row(InlineKeyboardButton("Анрег", callback_data=f"page_unregister:{page_number}"))
    else:
        markup.row(InlineKeyboardButton("Рег", callback_data=f"page_register:{page_number}"))
    markup.row(InlineKeyboardButton("Напомнить", callback_data=f"reminder:{page_number}"))
    text = str(get_event_by_page_number(page_number))
    if text != "None":
        await message.edit_text(str(get_event_by_page_number(page_number)), reply_markup=markup)
    else:
        await bot.answer_callback_query(callback_query_id=call_id, text="Такого мероприятия нет")


@dp.callback_query_handler(text_startswith="reminder")
async def process_reminder_callback(call: types.CallbackQuery):
    event_id = int(call.data.split(":")[1])
    event = get_event_by_page_number(event_id)
    start_date = datetime.fromisoformat(event[3].replace('T', ' '))
    remind_time = start_date - timedelta(hours=1)

    event_id = 1
    status = create_reminder_in_db(event_id, call.from_user['id'], remind_time)
    text = ""
    if status:
        text = "Напоминание уже установлено"
    else:
        text = f"Напоминание для мероприятия '{event[1]}' было установлено на {remind_time}"

    await bot.answer_callback_query(callback_query_id=call.id, text=text)


if __name__ == '__main__':
    executor.start_polling(dp)
