import asyncio
import logging
from time import sleep

from aiogram import Dispatcher

from bot_init import bot
from client.customer import router as clt_router
from client.staff_hotline import router as stf_htln_router

logging.basicConfig(level=logging.DEBUG,
                    filename="log.txt",
                    filemode="w"
                    )


async def main():
    dp = Dispatcher()
    dp.include_routers(clt_router, stf_htln_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())