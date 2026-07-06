import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram import F
from aiogram.types import Message
from aiohttp import web

from config.config import BOT_TOKEN, PORT
from database.db import init_db
from handlers import get_main_router
from payments.webhook import create_webhook_app
from services.daily_report_service import run_daily_report_scheduler
from services.expiration_service import run_expiration_checker
from services.reminder_service import run_reminder_checker
from utils.logger import setup_logging


async def run_webhook_server(bot: Bot) -> None:
    app = create_webhook_app(bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    await asyncio.Event().wait()


async def main() -> None:
    setup_logging()
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(get_main_router())

    debug_router = Router()

    @debug_router.message()
    async def debug_all(message):
        print("\n=== UPDATE ===")
        print("Chat ID:", message.chat.id)
        print("Type:", message.chat.type)
        print("Text:", message.text)

    dp.include_router(debug_router)

    await bot.delete_webhook(drop_pending_updates=True)

    await asyncio.gather(
        dp.start_polling(bot),
        run_webhook_server(bot),
        run_expiration_checker(bot),
        run_reminder_checker(bot),
        run_daily_report_scheduler(bot),
    )


if __name__ == "__main__":
    asyncio.run(main())
