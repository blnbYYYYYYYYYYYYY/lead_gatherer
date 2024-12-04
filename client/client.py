from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils import keyboard
from aiogram.methods import DeleteMessage

from filters.chat_type import ChatTypeFilter
from bot import bot, user_hotline_mode

router = Router()
router.message.filter(ChatTypeFilter(chat_type="private"))

def start_keyboard_builder(is_auth = None):
    kbd_buttons = [[
        types.InlineKeyboardButton(text="Задать вопрос", callback_data="start_hotline_chat")]]
    
    if is_auth == None:
      kbd_buttons[0].append(types.InlineKeyboardButton(text="Авторизоваться", callback_data="clt_auth"))

    return kbd_buttons

@router.message(F.func(lambda m: m.from_user.id in user_hotline_mode.keys()))
def hotline_chat(message: types.Message):
	print(message.text)
	user_hotline_mode[message.from_user.id] = message.md_text
      


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=start_keyboard_builder())

    await message.answer(text="Здравствуйте\!\nЯ \.\.\.\, администратор канала [Новостройки Москвы I ОЗ Лубянка](https://t.me/remarket_msk)\.\n"
                            f"Вы оставили ➕ под [постом](https://t.me/c/1697433693/6531)\.\n"
                            f"Нажмите на кнопку Авторизоваться, чтобы указать Ваш контактный номер телефона для связи\.\n\n"
                           f"На этот контактный номер телефона менеджер вышлет подробную презентацию о ЖК в мессенджер\,"
                         f"а также уточнит информацию по необходимым параметрам\, чтобы составить индивидуальную подборку точечно под Ваш запрос\.",
                         reply_markup=inline_keyboard)

    

@router.callback_query(F.data == "start_hotline_chat")
async def start_hotline_chat(callback: types.CallbackQuery):
	inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="Завершить диалог", callback_data="end_hotline_chat")]])
    
	await callback.message.edit_reply_markup()
	await callback.message.answer(text="Вы начали диалог с администратором бота 🙌")
	await callback.message.answer(text="Напишите свой вопрос и я отвечу Вам в ближайшее время\!", reply_markup=inline_keyboard)

	user_hotline_mode.setdefault(callback.message.from_user.id, "")

	"""
	start chat with staff_hotline
	... chating

	"""
     

@router.callback_query(F.data == "end_hotline_chat")
async def end_hotline_chat(callback: types.CallbackQuery):
	inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=start_keyboard_builder())
    
	await callback.message.edit_reply_markup()
	await callback.message.answer("Вы закончили диалог с администратором бота 👋", reply_markup=inline_keyboard)
     
	del user_hotline_mode[callback.message.from_user.id]

"""@router.message(F.text.lower() == "завершить диалог")
async def end_hotline_chat(message: types.Message):
	print(message.message_id)
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	await message.answer("Вы закончили диалог с администратором бота 👋", reply_markup=types.ReplyKeyboardRemove())"""
