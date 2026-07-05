from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config.config import SUBSCRIPTION_PRICE_MXN
from payments.mercadopago_client import create_payment_preference

router = Router()


@router.message(Command("suscribirme"))
async def cmd_subscribe(message: Message) -> None:
    payment_url = await create_payment_preference(message.from_user.id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Pagar ahora", url=payment_url)]
        ]
    )

    await message.answer(
        f"Suscripción mensual: ${SUBSCRIPTION_PRICE_MXN:.0f} MXN.\n"
        "Al confirmarse el pago recibirás un link de invitación de un solo uso al canal.",
        reply_markup=keyboard,
    )
