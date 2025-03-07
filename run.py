import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.redis import RedisStorage

from misc.bot import bot
from misc import db
from handlers.customer import router as clt_router
from handlers.staff_post import router as stf_pst_router
from handlers.staff_hotline import router as stf_htln_router

logging.basicConfig(level=logging.DEBUG,
                    filename="log.txt",
                    filemode="w",
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    )


async def main():
    dp = Dispatcher(
        storage=RedisStorage(redis=db.redis.Redis).from_url("redis://localhost:6379/5"), 
        fsm_strategy=FSMStrategy.USER_IN_CHAT
    )
    dp.include_routers(stf_pst_router, clt_router, stf_htln_router)

    await dp.start_polling(bot, handle_signals=False)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot stopped")