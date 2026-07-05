from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

WELCOME_MESSAGE = (
    "Bienvenido a mi canal premium, por fin encontraste lo que llevas "
    "buscando tanto tiempo, espero te encante:D"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_MESSAGE)
