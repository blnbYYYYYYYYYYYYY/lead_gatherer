import asyncio
import logging
from time import sleep

from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import config
from client import client, staff_hotline, staff_post

logging.basicConfig(level=logging.DEBUG,
                    filename="log.txt",
                    filemode="w"
                    )

bot = Bot(token=config.bot_token.get_secret_value(),
          default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2, link_preview_is_disabled=True))

user_hotline_mode = {}

async def main():
    dp = Dispatcher()
    dp.include_router(client.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())