from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Text
from aiogram.fsm.context import FSMContext

from misc.db import get_data
from misc.bot import bot, HotLine
from misc.opt import texts, keyboards
from misc.util import content_types, update_keyboard
from misc.filters import ChatTypeFilter, IsStaffFilter, IsAllowed, IsHotlineMode


router = Router() # создание роутера сообщений для горячей линии
router.message.filter(ChatTypeFilter(chat_type="supergroup"), IsStaffFilter()) 
# применение фильтра супергрупп и стафф фильтра к роутеру


@router.message(IsAllowed(allowed_content_types=content_types), IsHotlineMode()) # роутер с фильтром типов сообщений
async def redirect_staff_message(message: types.Message, state: FSMContext):
    chat_id = await get_data(message.message_thread_id)

    code_to_execute = """bot.send_{0}(
                            {1}, 
                            chat_id={2}
                        )"""
    # команда для отправления сообщений разных типов, сделано для сокращения

    content_type = str(message.content_type).split(".")[1].lower()
    # сохранение типа контента в отдельную переменную

    # удаление инлайн клавиатуры с последнего сообщения в чате клиента с ботом

    if content_type in ("venue", "location", "poll"):
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await message.answer(**texts.as_wrong_type.as_kwargs())
        return 0
        # если тип контента локация в двух ее разновидностях, то бот удаляет это сообщение
        # и отправляет предупреждение

    elif content_type == "text":
        content = message.md_text
        message_answer = await eval(code_to_execute.format(
            "message", 
            "text=content", 
            chat_id))
        # если тип контента текст, то динамически выполняется строка с подставленными значениями 
        # "message", "text", "text", chat_id по порядку, а затем объект message сохраняется в переменную

    elif content_type == "photo":
        message_answer = await eval(code_to_execute.format(
            content_type, 
            f"{content_type}=message.{content_type}[-1].file_id",
            chat_id))
    else:
        message_answer = await eval(code_to_execute.format(
            content_type, 
            f"{content_type}=message.{content_type}.file_id",
            chat_id))
        # если прислали другие типы контента 
        # (в нашем случае это "sticker", "animation", "photo", "video", "voice", "video_note", "contact"), 
        # то динамически выполняется строка с подставленными значениями 
        # content_type, content_type, content_type + ".file_id", chat_id по порядку
        # (content_type + ".file_id" т.к. мы отправляем контент, который прежде загрузили на сервер тг), 
        # а затем объект message сохраняется в переменную

    await update_keyboard(message_answer.message_id, state, keyboards.ik_end_chat)
    # обновляем id сообщения, на котором висит инлайн клавиатура в чате клиента с ботом
