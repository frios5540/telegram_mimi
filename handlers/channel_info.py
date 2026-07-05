import logging

from aiogram import Router
from aiogram.types import Message

router = Router()
logger = logging.getLogger(__name__)


@router.channel_post()
async def log_channel_id(message: Message) -> None:
    logger.info(
        "Canal detectado -> título: %s | ID: %s",
        message.chat.title,
        message.chat.id,
    )
