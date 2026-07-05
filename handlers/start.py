from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

WELCOME_MESSAGE = (
    "🐰 Bienvenido a mi VIP 🐰

Aquí podrás acceder al contenido mas exclusivo que tanto has buscado 💙.

Usa /suscribirme para obtener tu acceso mensual ⭐"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_MESSAGE)
