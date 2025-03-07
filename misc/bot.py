from misc.config import config
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


bot = Bot(
	token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(
		parse_mode=ParseMode.MARKDOWN_V2, 
		link_preview_is_disabled=True))