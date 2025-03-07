from aiogram import types
from aiogram.utils.formatting import Text

ik_end_chat = types.InlineKeyboardMarkup(
	inline_keyboard=[[types.InlineKeyboardButton(
		text="Завершить диалог", 
		callback_data="end_hotline"
		)]])


def ikb_default(is_verified: int = None) -> types.InlineKeyboardMarkup:
	buttons = [[
		types.InlineKeyboardButton(**Text("Задать вопрос").as_kwargs(), callback_data="start_hotline")]]
	
	if is_verified:
		content = Text("✅ Оставить номер")
	else:
		content = Text("Оставить номер")
	
	buttons[0].append(types.InlineKeyboardButton(**content.as_kwargs(), callback_data="verify_number"))
	
	return types.InlineKeyboardMarkup(inline_keyboard=buttons)

rk_share_contact = types.ReplyKeyboardMarkup(
		keyboard=[[types.KeyboardButton(
			text="Поделиться контактом", 
			request_contact=True
			)]], 
		input_field_placeholder="Введите номер...",
		resize_keyboard=True
		)

ik_auth = types.InlineKeyboardMarkup(
	inline_keyboard=[
		[
			types.InlineKeyboardButton(
				text="Звонок", 
				callback_data="contact_call"
			),
			types.InlineKeyboardButton(
				text="Мессенджер", 
				callback_data="contact_chat"
			)
		],
		[
			types.InlineKeyboardButton(
				text="Номер не верный", 
				callback_data="clt_auth")
		]
	]
)

def ikb_ref(message_id: types.message_id) -> types.InlineKeyboardMarkup:
	return types.InlineKeyboardMarkup(
		inline_keyboard=[
			[
				types.InlineKeyboardButton(
					text="➕", 
					url=f"https://t.me/lead_gatherer_bot?start=request_{message_id}"
				)
			]
		]
	)
