import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMedia, InputMediaPhoto, InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import exceptions

from db import get_event_by_page_number, get_event_object_by_page_number, get_events_count, check_user_registration, register_user, unregister_user, create_record, create_reminder_in_db, checker
from cfg import API_TOKEN, IMG_SAVE_PATH


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.callback_query_handler(text_startswith="page_prev")
async def handle_prev_page(call: types.CallbackQuery):
    page_number = int(call.data.split(":")[1]) - 1
    if page_number < 1:
        last_page_number = get_events_count()
        await update_page_markup(call.message, call.from_user['id'], call.id, last_page_number)
    else:
        await update_page_markup(call.message, call.from_user['id'], call.id, page_number)


@dp.callback_query_handler(text_startswith="page_next")
async def handle_next_page(call: types.CallbackQuery):
    page_number = int(call.data.split(":")[1]) + 1
    await update_page_markup(call.message, call.from_user['id'], call.id, page_number)


@dp.callback_query_handler(text_startswith="page_register")
async def handle_register_user(call: types.CallbackQuery):
    page_number = int(call.data.split(":")[1])
    event_id = get_event_object_by_page_number(page_number)[0]
    register_user(call.from_user['id'], event_id)
    await update_page_markup(call.message, call.from_user['id'], call.id, page_number)


@dp.callback_query_handler(text_startswith="page_unregister")
async def handle_unregister_user(call: types.CallbackQuery):
    page_number = int(call.data.split(":")[1])
    event_id = get_event_object_by_page_number(page_number)[0]
    unregister_user(call.from_user['id'], event_id)
    await update_page_markup(call.message, call.from_user['id'], call.id, page_number)


@dp.message_handler(commands=["start"])
async def handle_start_command(msg: types.Message):
    page_number = 1
    event_id = get_event_object_by_page_number(page_number)[0]
    if_exists, is_registered = check_user_registration(chat_id=msg.from_id, event_id=event_id)
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Назад", callback_data=f"page_prev:0"),
        InlineKeyboardButton("Вперёд", callback_data=f"page_next:1"),
    )

    if not if_exists:
        create_record(msg.from_id, event_id)

    if is_registered:
        markup.row(InlineKeyboardButton("Анрег", callback_data=f"page_unregister:1"))
    else:
        markup.row(InlineKeyboardButton("Рег", callback_data=f"page_register:1"))
    event_text, event_img_link = get_event_by_page_number(page_number)
    if event_img_link != "":
        event_img_link = IMG_SAVE_PATH + event_img_link
    else:
        event_img_link = IMG_SAVE_PATH + "placeholder.jpg"
    await msg.answer_photo(photo=InputFile(event_img_link), caption=event_text, reply_markup=markup, parse_mode="Markdown")


async def update_page_markup(message, user_id, call_id, page_number):
    event_id = get_event_object_by_page_number(page_number)[0]
    if_exists, is_registered = check_user_registration(chat_id=user_id, event_id=event_id)
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Назад", callback_data=f"page_prev:{page_number}"),
        InlineKeyboardButton("Вперёд", callback_data=f"page_next:{page_number}")
    )

    if is_registered:
        markup.row(InlineKeyboardButton("Анрег", callback_data=f"page_unregister:{page_number}"))
    else:
        markup.row(InlineKeyboardButton("Рег", callback_data=f"page_register:{page_number}"))
    text = str(get_event_by_page_number(page_number))
    if text != "None":
        if not if_exists:
            create_record(user_id, event_id)
        event_text, event_img_link = get_event_by_page_number(page_number)
        if event_img_link != "":
            event_img_link = IMG_SAVE_PATH + event_img_link
        else:
            event_img_link = IMG_SAVE_PATH + "placeholder.jpg"
        event_img_file = InputMediaPhoto(media=InputFile(event_img_link), caption=event_text, parse_mode="Markdown")

        await message.edit_media(event_img_file, reply_markup=markup)
    else:
        await update_page_markup(message, user_id, call_id, page_number=1)


@dp.callback_query_handler(text_startswith="reminder")
async def process_reminder_callback(call: types.CallbackQuery):
    event_id = int(call.data.split(":")[1])
    event = get_event_object_by_page_number(event_id)
    start_date = datetime.fromisoformat(event[6].replace('T', ' '))
    remind_time = start_date - timedelta(hours=1)
    status = create_reminder_in_db(event_id, call.from_user['id'], remind_time)
    text = ""
    if status:
        text = "Напоминание уже установлено"
    else:
        text = f"Напоминание для мероприятия '{event[1]}' было установлено на {remind_time}"

    await bot.answer_callback_query(callback_query_id=call.id, text=text)


# Функция для проверки времени напоминания
async def check_reminders():
    while True:
        user_id = checker()
        if user_id is not None:
            await send_reminder(user_id)
        # Ждем 1 секунду перед следующей проверкой
        await asyncio.sleep(1)


# Функция для отправки напоминания (дописать напоминание чего)
async def send_reminder(user_id):
    try:
        await bot.send_message(chat_id=user_id, text="Напоминание!")
    except exceptions.BotBlocked:
        print(f"Бот заблокирован пользователем {user_id}")
    except exceptions.ChatNotFound:
        print(f"Чат не найден, chat_id={user_id}")


async def main():
    await check_reminders()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    executor.start_polling(dp)
