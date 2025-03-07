from aiogram import Router, types, F

from misc.bot import bot
from misc.opt import keyboards
from misc.config import config
from misc.filters import ChatTypeFilter, IsStaffFilter

router = Router()
router.message.filter(ChatTypeFilter(chat_type="supergroup"), IsStaffFilter(mode="post"))


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

    """
    сначала отправляет сообщение в канал, а затем добавляет 
    к нему клавиатуру с реферальной ссылкой на пост
    """

