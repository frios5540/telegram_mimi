import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from config.config import CHANNEL_ID
from database.subscriptions import get_expired_subscriptions, mark_expired

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 60 * 60


async def _remove_user(bot: Bot, user_id: int) -> None:
    try:
        await bot.ban_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        await bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    except TelegramBadRequest:
        logger.info("El usuario %s ya no estaba en el canal", user_id)

    try:
        await bot.send_message(
            user_id, "Tu suscripción al canal premium venció. ¡Vuelve con /suscribirme!"
        )
    except TelegramBadRequest:
        pass


async def run_expiration_checker(bot: Bot) -> None:
    while True:
        expired = await get_expired_subscriptions(datetime.now(timezone.utc))
        for subscription in expired:
            user_id = subscription["user_id"]
            await _remove_user(bot, user_id)
            await mark_expired(user_id)
            logger.info("Suscripción vencida y usuario removido: %s", user_id)

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
