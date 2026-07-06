from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config.config import ADMIN_TELEGRAM_ID
from services.daily_report_service import build_daily_report

router = Router()


@router.message(Command("reporte"))
async def cmd_report(message: Message) -> None:
    if ADMIN_TELEGRAM_ID is None or message.from_user.id != ADMIN_TELEGRAM_ID:
        return

    report = await build_daily_report()
    await message.answer(report)
