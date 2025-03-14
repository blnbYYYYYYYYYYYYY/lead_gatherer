from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text
from aiogram.fsm.context import FSMContext

from misc.db import get_value
from misc.bot import bot, HotLine
from misc.opt import texts, keyboards
from misc.util import user_content_types, update_keyboard, redirect_message
from misc.filters import ChatTypeFilter, IsStaffFilter, IsAllowedContentFilter, IsHotlineModeFilter


router = Router() # создание роутера сообщений для горячей линии
router.message.filter(ChatTypeFilter(chat_type="supergroup"), IsStaffFilter()) 
# применение фильтра супергрупп и стафф фильтра к роутеру


@router.message(IsAllowedContentFilter(allowed_content_types=user_content_types), IsHotlineModeFilter()) # роутер с фильтром типов сообщений
async def redirect_staff_message(message: types.Message, state: FSMContext):
    chat_id = await get_value(
        message.message_thread_id, 
        "chat_id")
    ik_message_id = await get_value(
        int(chat_id), 
        "ik_message_id")
    message_answer = await redirect_message(
        message,
        chat_id)

    if message_answer.text == message.text:
        await update_keyboard(
            current_message_id=message_answer.message_id,
            previous_message_id=ik_message_id,
            chat_id=chat_id,
            reply_markup=keyboards.ik_end_chat)
