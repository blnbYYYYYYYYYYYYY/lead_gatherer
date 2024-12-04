from aiogram import F, Router, types
from aiogram.filters import Command

from filters.chat_type import ChatTypeFilter
from config import config
from bot_init import bot


router = Router()
router.message.filter(ChatTypeFilter(chat_type="private"))


hotline_chat = {}
inline_keyboard_msg_id = {}
allowed_content_types = ("text", "sticker", "animation", "photo", "video", "voice", "contact", "location")
inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="Завершить диалог", callback_data="end_hotline_chat")]])


def start_keyboard_builder(is_auth = None):
	kbd_buttons = [[
		types.InlineKeyboardButton(text="Задать вопрос", callback_data="start_hotline_chat")]]
	
	if is_auth == None:
		kbd_buttons[0].append(types.InlineKeyboardButton(text="Авторизоваться", callback_data="clt_auth"))
	
	return kbd_buttons


@router.message(lambda m: m.from_user.full_name in hotline_chat.keys())
async def send_msg_to_htln(message: types.Message):

	code_to_execute = """bot.send_{0}({1}=message.{2}, chat_id=config.superchat_id.get_secret_value(), message_thread_id=hotline_chat[message.from_user.full_name]["thread_id"])"""
	
	content_type = str(message.content_type).split(".")[1].lower()

	print(content_type)
	
	if content_type == "text":
		await eval(code_to_execute.format("message", "text", "text"))

	elif content_type in ("venue", "location"):
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
		await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=inline_keyboard_msg_id[message.chat.id], reply_markup=None)
		await message.answer(text="Обмен геолокацией не поддерживается", reply_markup=inline_keyboard)
		inline_keyboard_msg_id.update({message.chat.id: message.message_id})

	else:
		await eval(code_to_execute.format(content_type, content_type, content_type + ".file_id"))


@router.message(Command("start"))
async def cmd_start(message: types.Message):
	inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=start_keyboard_builder())

	await message.answer(text="Здравствуйте\!\nЯ \.\.\.\, администратор канала [Новостройки Москвы I ОЗ Лубянка](https://t.me/remarket_msk)\.\n"
		f"Вы оставили ➕ под [постом](https://t.me/c/1697433693/6531)\.\n"
		f"Нажмите на кнопку Авторизоваться, чтобы указать Ваш контактный номер телефона для связи\.\n\n"
		f"На этот контактный номер телефона менеджер вышлет подробную презентацию о ЖК в мессенджер\,"
		f"а также уточнит информацию по необходимым параметрам\, чтобы составить индивидуальную подборку точечно под Ваш запрос\.",
		reply_markup=inline_keyboard)
	inline_keyboard_msg_id.update({message.chat.id: message.message_id})

	

@router.callback_query(F.data == "start_hotline_chat")
async def start_hotline_chat(callback: types.CallbackQuery):	
	await callback.message.edit_reply_markup()
	await callback.message.answer(text="Вы начали диалог с администратором бота 🙌")
	await callback.message.answer(
		text="Напишите свой вопрос и я отвечу Вам в ближайшее время\!", 
		reply_markup=inline_keyboard
		)
	inline_keyboard_msg_id.update({callback.message.chat.id: callback.message.message_id})
	
	try:
		bot.close_forum_topic(
			chat_id=config.superchat_id.get_secret_value(),
			message_thread_id=hotline_chat[callback.from_user.full_name]["thread_id"]
			)
		bot.reopen_forum_topic(
			chat_id=config.superchat_id.get_secret_value(),
			message_thread_id=hotline_chat[callback.from_user.full_name]["thread_id"]
			)
	except:
		topic = await bot.create_forum_topic(
			chat_id=config.superchat_id.get_secret_value(), 
			name=str(callback.from_user.full_name)
			)
	
		hotline_chat.setdefault(callback.from_user.full_name, 
			{
			"chat_id": callback.message.chat.id, 
			"thread_id": topic.message_thread_id
			}
			)
	
	await bot.send_message(
		text=f"{callback.from_user.full_name}, {callback.from_user.id}, {callback.from_user.username},\
			{callback.from_user.is_premium}, {callback.from_user.model_extra}",
		chat_id=config.superchat_id.get_secret_value(), 
		message_thread_id=hotline_chat[callback.from_user.full_name]["thread_id"],
		parse_mode="HTML"
		)

	 

@router.callback_query(F.data == "end_hotline_chat")
async def end_hotline_chat(callback: types.CallbackQuery):
	inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=start_keyboard_builder())

	await callback.message.edit_reply_markup()
	await callback.message.answer("Вы закончили диалог с администратором бота 👋", reply_markup=inline_keyboard)
	inline_keyboard_msg_id.update({callback.message.chat.id: callback.message.message_id})
	


