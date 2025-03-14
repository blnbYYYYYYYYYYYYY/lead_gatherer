import os

from typing import Union
from misc.db import get_value

from aiogram.types import Message
from aiogram.filters import BaseFilter


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class IsStaffFilter(BaseFilter):
    def __init__(self, mode: Union[str, None] = None):
        self.mode = mode 
        self.superchat_id = os.getenv("SUPERCHAT_ID")

    async def __call__(self, message: Message) -> bool:
        if str(message.chat.id) == self.superchat_id:
            if self.mode == "post":
                return message.message_thread_id == None    # т.к. постим через дженерал топик, а у него айди нан
            else:
                return message.message_thread_id != None
        else:
            return False

class IsAllowedContentFilter(BaseFilter):
    def __init__(self, allowed_content_types: Union[str, list, tuple] = None):
        self.content_type = allowed_content_types

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.content_type, str):
            return str(message.content_type).split(".")[1].lower() == self.content_type
        else:
            return str(message.content_type).split(".")[1].lower() in self.content_type
        
    async def filter(message: Message, content_type: str) -> bool:
        return str(message.content_type).split(".")[1].lower() == content_type
        

class IsHotlineModeFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        chat_id = await get_value(message.message_thread_id, "chat_id")
        return int(chat_id) > 0 