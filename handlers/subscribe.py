import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config.config import SUBSCRIPTION_PRICE_MXN
from payments.mercadopago_client import create_payment_preference

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("suscribirme"))
async def cmd_subscribe(message: Message) -> None:
    try:
        payment_url = await create_payment_preference(message.from_user.id)
    except Exception:
        logger.exception(
            "No se pudo generar el link de pago para el usuario %s", message.from_user.id
        )
        await message.answer(
            "Las suscripciones están pausadas temporalmente. Vuelve a intentarlo más tarde 🙏"
        )
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Pagar ahora", url=payment_url)]
        ]
    )

    await message.answer(
        f"Suscripción mensual: ${SUBSCRIPTION_PRICE_MXN:.0f} MXN.\n"
        "Al confirmarse el pago recibirás un link de invitación al canal el cual asegura tu suscripción por un mes 💙⭐",
        reply_markup=keyboard,
    )
