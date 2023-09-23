import sqlite3

from aiogram import Bot, Dispatcher, executor

from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next, Button,Cancel
from aiogram_dialog.widgets.text import Const



storage = MemoryStorage()
bot = Bot(token='6325210305:AAGZSFpDyFn2bfuH8jujhs6I_Ms5Pa9ZwTo')
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)

conn = sqlite3.connect('tulaevents.db',check_same_thread=False)
cursor = conn.cursor()

class EventRegistrationForm(StatesGroup):
    start = State()
    age_limit= State()
    format = State()
    company = State()
    categoty = State()
    date_time = State()
    registration_of_participants = State()

async def on_input(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await dialog.next()  # rendering tool cannot detect this call

async def final_input(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await m.answer("Регистрация окончена!")
    await dialog.switch_to(state=EventRegistrationForm.start)
    
async def go_back(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().back()


async def go_next(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.dialog().next()

dialog = Dialog(
    Window(
        Const("Начало регистрация мероприятия"),
        Button(Const("Next"), id="next", on_click=go_next),
        state = EventRegistrationForm.start,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Возрастные ограничения"),
        Button(Const("Back"), id="backStart", on_click=go_back),
        MessageInput(on_input),
        state=EventRegistrationForm.age_limit,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Формат мероприятия"),
        Button(Const("Back"), id="backFio", on_click=go_back),
        MessageInput(on_input),
        state = EventRegistrationForm.format,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Компания проводящая ивент"),
        Button(Const("Back"), id="backLoc", on_click=go_back),
        MessageInput(on_input),
        state = EventRegistrationForm.company,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Категория"),
        Button(Const("Back"), id="backTime", on_click=go_back),
        MessageInput(on_input),
        state = EventRegistrationForm.categoty,
        preview_add_transitions=[Next()],
    ),Window(
        Const("Дата/время проведения"),
        Button(Const("Back"), id="backTime", on_click=go_back),
        MessageInput(on_input),
        state = EventRegistrationForm.date_time,
        preview_add_transitions=[Next()],
    ),
    Window(
        Const("Требуется ли запись участников?( да/нет )"),
        Button(Const("Back"), id="backPay", on_click=go_back),
        MessageInput(final_input),
        state = EventRegistrationForm.registration_of_participants,
        preview_add_transitions=[Cancel()]
    ),

)

registry.register(dialog)
#render_transitions([dialog])

@dp.message_handler(commands=["start"])
async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(EventRegistrationForm.start, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    