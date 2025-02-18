from aiogram import Router, types

from aiogram.utils.formatting import Text
from aiogram.enums import ParseMode
# нужно для экзэк/эвал

from filters.filters import ChatTypeFilter, IsStaffFilter, IsAllowed
from bot_init import bot
from client.customer import hotline_chat, inline_keyboard_msg_id
from opt import keyboards

router = Router() # создание роутера сообщений для горячей линии
router.message.filter(ChatTypeFilter(chat_type="supergroup"), IsStaffFilter()) 
# применение фильтра супергрупп и стафф фильтра к роутеру

content_types = (
    "text", "sticker", "animation", "photo", 
    "video", "voice", "video_note", "contact", 
    "location", "venue", "document"
)
# разрешенные типы сообщений, т.к. не нашел другого способа игнорировать сервисные сообщения


@router.message(IsAllowed(allowed_content_types=content_types)) # роутер с фильтром типов сообщений
async def answer_to_clt(message: types.Message):

    try:

        chat_id: int

        for c_id, t_id in hotline_chat.items():

            if t_id == message.message_thread_id:
                chat_id = c_id

                break
        # пытаюсь проитерировать id тем супергруппы и найти соответсвующий id чата

    except TypeError as _:

        if len(hotline_chat.keys()) == 1:
            chat_id = int(list(hotline_chat.keys())[0])

        # если возникает ошибка при итерации, значит запись в словаре одна и можно ее просто достать


    code_to_execute = """bot.send_{0}(
                            {1}, 
                            chat_id={2}, 
                            reply_markup=keyboards.ik_end_chat
                        )"""
    # команда для отправления сообщений разных типов, сделано для сокращения

    content_type = str(message.content_type).split(".")[1].lower()
    # сохранение типа контента в отдельную переменную

    await bot.edit_message_reply_markup(
        chat_id=chat_id, 
        message_id=inline_keyboard_msg_id[chat_id], 
        reply_markup=None
    )	
    # удаление инлайн клавиатуры с последнего сообщения в чате клиента с ботом

    if content_type == "text":
        content = message.md_text
        htln_message = await eval(
            code_to_execute.format(
                "message", 
                "text=content", 
                chat_id
            )
        )
        # если тип контента текст, то динамически выполняется строка с подставленными значениями 
        # "message", "text", "text", chat_id по порядку, а затем объект message сохраняется в переменную

    elif content_type in ("venue", "location", "poll"):
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await message.answer(text="Упссс... Что-то пошло не так...:((")
        # если тип контента локация в двух ее разновидностях, то бот удаляет это сообщение
        # и отправляет предупреждение
    elif content_type == "photo":
        htln_message = await eval(
            code_to_execute.format(
                content_type, 
                f"{content_type}=message.{content_type}[-1].file_id",
                chat_id
            )
        )
    else:
        htln_message = await eval(
            code_to_execute.format(
                content_type, 
                f"{content_type}=message.{content_type}.file_id",
                chat_id
            )
        )
        # если прислали другие типы контента 
        # (в нашем случае это "sticker", "animation", "photo", "video", "voice", "video_note", "contact"), 
        # то динамически выполняется строка с подставленными значениями 
        # content_type, content_type, content_type + ".file_id", chat_id по порядку
        # (content_type + ".file_id" т.к. мы отправляем контент, который прежде загрузили на сервер тг), 
        # а затем объект message сохраняется в переменную

    inline_keyboard_msg_id.update({chat_id: htln_message.message_id})
    # обновляем id сообщения, на котором висит инлайн клавиатура в чате клиента с ботом
