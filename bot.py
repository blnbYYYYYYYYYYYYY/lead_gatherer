import asyncio
import logging

from aiogram import Dispatcher

from bot_init import bot, io_json
from client.customer import router as clt_router
from client.customer import hotline_chat, inline_keyboard_msg_id, auth_status, refs
from client.staff_hotline import router as stf_htln_router
from client.staff_post import router as stf_pst_router

logging.basicConfig(level=logging.DEBUG,
                    filename="log.txt",
                    filemode="w"
                    )


async def main():
    dp = Dispatcher()
    dp.include_routers(stf_pst_router, clt_router, stf_htln_router)

    await dp.start_polling(bot, handle_signals=False)



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        io_json(variable="hotline_chat", mode="w", data=hotline_chat)
        io_json(variable="inline_keyboard_msg_id", mode="w", data=inline_keyboard_msg_id)
        io_json(variable="auth_status", mode="w", data=auth_status)
        io_json(variable="refs", mode="w", data=refs)
        