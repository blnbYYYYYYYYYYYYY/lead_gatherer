from aiogram import Router, types, F
from aiogram.utils.formatting import Text

from filters.filters import ChatTypeFilter, IsStaffFilter
from bot_init import bot # импортирую объект бота из инициализирующего файла
from client.customer import hotline_chat, inline_keyboard_msg_id
from opt import keyboards
from config import config
# импортирую словари для сопоставления и объект текущей инлайн клавиатуры

router = Router() # создание роутера сообщений для горячей линии
router.message.filter(ChatTypeFilter(chat_type="supergroup"), IsStaffFilter(mode="post")) # применение фильтра супергрупп к роутеру

@router.message(F.text)
async def redirect_to_channel(message: types.Message):
    channel_message = await bot.send_message(
        chat_id=config.channel_id.get_secret_value(), 
        text=message.md_text
    )
    await bot.edit_message_reply_markup(
        chat_id=config.channel_id.get_secret_value(), 
        message_id=channel_message.message_id,
        reply_markup=keyboards.ikb_ref(channel_message.message_id)
    )

