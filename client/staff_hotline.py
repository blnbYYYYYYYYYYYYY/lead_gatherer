from aiogram import F, Router, types

from filters.chat_type import ChatTypeFilter
from bot_init import bot
from client.customer import hotline_chat

router = Router()
router.message.filter(ChatTypeFilter(chat_type="supergroup"))

allowed_content_types = ("text", "sticker", "animation", "photo", "video", "voice", "contact", "location")

@router.message(lambda m: str(m.content_type).split(".")[1].lower() in allowed_content_types)
async def answer_to_clt(message: types.Message):
    print(message.content_type)
    await message.answer("\:\)")

