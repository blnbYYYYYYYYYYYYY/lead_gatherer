import os
from dotenv import load_dotenv
from typing import Union, NamedTuple

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties


class Contact(NamedTuple):
    full_name: Union[str, None]
    phone_number: Union[str, None]


class HotLine(StatesGroup):
	enabled = State()


class Verification(StatesGroup):
	share_contact = State()
	share_name = State()


class Post(StatesGroup):
	share_post = State()

load_dotenv(".env")

bot = Bot(
	token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(
		parse_mode=ParseMode.MARKDOWN_V2, 
		link_preview_is_disabled=True))