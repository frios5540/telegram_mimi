"""Script temporal para obtener el ID de un canal. Bórralo cuando ya no lo necesites."""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message

from config.config import BOT_TOKEN

dp = Dispatcher()


@dp.channel_post()
async def print_channel_id(message: Message) -> None:
    print(f"Canal: {message.chat.title} | ID: {message.chat.id}")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Esperando mensajes del canal... publica algo para ver su ID.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
