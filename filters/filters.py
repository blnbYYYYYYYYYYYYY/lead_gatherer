from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import config


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
        self.superchat_id = config.superchat_id.get_secret_value()

    async def __call__(self, message: Message) -> bool:
        if str(message.chat.id) == self.superchat_id:
            if self.mode == "post":
                return message.message_thread_id == None
            else:
                return message.message_thread_id != None
        else:
            return False

class IsAllowed(BaseFilter):
    def __init__(self, allowed_content_types: Union[str, list, tuple] = None):
        self.content_type = allowed_content_types

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.content_type, str):
            return str(message.content_type).split(".")[1].lower() == self.content_type
        else:
            return str(message.content_type).split(".")[1].lower() in self.content_type
        

class IsHotlineMode(BaseFilter):
    def __init__(self, hotline_chat):
        self.hotline_chat = hotline_chat

    async def __call__(self, message: Message) -> bool:
        if message.chat.id in self.hotline_chat.keys():
            return self.hotline_chat[message.chat.id] > 0
        else:
            return False
