import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from database.subscriptions import get_subscriptions_due_for_reminder, mark_reminder_sent

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 60 * 60

REMINDER_MESSAGE = (
    "⏰ Tu suscripción a BunnyMimii VIP vence mañana.\n\n"
    "Para mantener tu acceso al canal privado, renueva tu mensualidad usando /suscribirme."
)


async def run_reminder_checker(bot: Bot) -> None:
    while True:
        now = datetime.now(timezone.utc)
        due = await get_subscriptions_due_for_reminder(now)
        for subscription in due:
            user_id = subscription["user_id"]
            try:
                await bot.send_message(user_id, REMINDER_MESSAGE)
                await mark_reminder_sent(user_id, now)
                logger.info(
                    "Recordatorio de renovación enviado a %s (vence %s)",
                    user_id,
                    subscription["expires_at"],
                )
            except TelegramBadRequest:
                logger.warning("No se pudo enviar recordatorio a %s", user_id)

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
