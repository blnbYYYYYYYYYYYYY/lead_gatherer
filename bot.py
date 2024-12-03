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
import client

logging.basicConfig(level=logging.DEBUG,
                    filename="log.txt",
                    filemode="w"
                    )


async def main():
    bot = Bot(token=config.bot_token.get_secret_value(),
          default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
    dp = Dispatcher()
    dp.include_router(client.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())