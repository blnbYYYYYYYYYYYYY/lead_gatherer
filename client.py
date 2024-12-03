from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils import keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    inline_button = types.InlineKeyboardMarkup(inline_keyboard=types.InlineKeyboardButton(text="Задать вопрос", callback_data="clt_ask"))
    button = types.ReplyKeyboardMarkup(keyboard=types.KeyboardButton(text="Авторизоваться", request_contac=True))

    await message.answer(text="Здравствуйте\!\nЯ \.\.\.\, администратор канала [Новостройки Москвы I ОЗ Лубянка](https://t.me/remarket_msk)\.\n"
                            f"Вы оставили ➕ под [постом](https://t.me/c/1697433693/6531)\.\n"
                            f"Нажмите на кнопку Авторизоваться, чтобы указать Ваш контактный номер телефона для связи\.\n\n"
                           f"На этот контактный номер телефона менеджер вышлет подробную презентацию о ЖК в мессенджер\,"
                         f"а также уточнит информацию по необходимым параметрам\, чтобы составить индивидуальную подборку точечно под Ваш запрос\.",
                         reply_markup=(inline_button, button))