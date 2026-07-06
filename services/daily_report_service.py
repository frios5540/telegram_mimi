import asyncio
import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from aiogram import Bot

from config.config import ADMIN_TELEGRAM_ID, SUBSCRIPTION_PRICE_MXN
from database.subscriptions import (
    count_active_expiring_within,
    count_active_subscriptions,
    count_expired_subscriptions,
    count_payments_since,
)

logger = logging.getLogger(__name__)

MEXICO_CITY_TZ = ZoneInfo("America/Mexico_City")
REPORT_HOUR = 9


def _start_of_today_mexico_city(now_utc: datetime) -> datetime:
    now_mx = now_utc.astimezone(MEXICO_CITY_TZ)
    start_mx = now_mx.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_mx.astimezone(timezone.utc)


async def build_daily_report() -> str:
    now = datetime.now(timezone.utc)

    # "Nuevos suscriptores" cuenta pagos (altas o renovaciones) en la ventana.
    # La tabla `subscriptions` sobrescribe paid_at en cada renovación y no
    # tiene un campo `first_paid_at` ni un historial de pagos separado, así
    # que no se puede distinguir una alta nueva de una renovación con el
    # esquema actual.
    new_subscribers_24h = await count_payments_since(now - timedelta(hours=24))

    # Ingreso estimado = pagos en la ventana * precio fijo actual.
    # Para un monto exacto por pago (si el precio llegara a cambiar) haría
    # falta guardar el `transaction_amount` real de cada pago de Mercado
    # Pago, lo cual implicaría tocar payments/webhook.py.
    revenue_24h = new_subscribers_24h * SUBSCRIPTION_PRICE_MXN

    active_total = await count_active_subscriptions()
    expired_total = await count_expired_subscriptions()

    expiring_24h = await count_active_expiring_within(now, timedelta(hours=24))
    expiring_3d = await count_active_expiring_within(now, timedelta(days=3))

    payments_today = await count_payments_since(_start_of_today_mexico_city(now))

    # payments/webhook.py ya detecta duplicados vía payment_already_processed()
    # pero solo los ignora (early return) sin registrar el evento en ningún
    # lado consultable. Haría falta una tabla de auditoría (o loguearlo) para
    # poder contarlos aquí sin modificar la lógica del webhook.
    duplicate_payments = "No disponible"

    # Los errores del webhook (firma inválida, pago no aprobado, excepciones)
    # solo se registran con logger.warning/logger.error hacia stdout; no se
    # persisten en la base de datos. Haría falta una tabla `webhook_errors`
    # (o similar) para poder reportarlos aquí.
    webhook_errors = "No disponible"

    return (
        "📊 Reporte diario - Canal VIP\n\n"
        f"🆕 Nuevos suscriptores (últimas 24h): {new_subscribers_24h}\n"
        f"💰 Ingresos estimados (últimas 24h): ${revenue_24h:.0f} MXN\n"
        f"✅ Suscriptores activos: {active_total}\n"
        f"❌ Suscripciones vencidas (total): {expired_total}\n"
        f"⏰ Vencen en próximas 24h: {expiring_24h}\n"
        f"📅 Vencen en próximos 3 días: {expiring_3d}\n"
        f"💳 Pagos aprobados hoy: {payments_today}\n"
        f"🔁 Pagos duplicados/ignorados: {duplicate_payments}\n"
        f"⚠️ Errores recientes del webhook: {webhook_errors}"
    )


async def send_daily_report(bot: Bot) -> None:
    if ADMIN_TELEGRAM_ID is None:
        logger.warning("ADMIN_TELEGRAM_ID no está configurado, no se envía el reporte diario")
        return

    try:
        report = await build_daily_report()
        await bot.send_message(ADMIN_TELEGRAM_ID, report)
        logger.info("Reporte diario enviado a admin %s", ADMIN_TELEGRAM_ID)
    except Exception:
        logger.exception("Error al generar/enviar el reporte diario")


def _seconds_until_next_report(now_utc: datetime) -> float:
    now_mx = now_utc.astimezone(MEXICO_CITY_TZ)
    target_mx = now_mx.replace(hour=REPORT_HOUR, minute=0, second=0, microsecond=0)
    if target_mx <= now_mx:
        target_mx += timedelta(days=1)
    return (target_mx.astimezone(timezone.utc) - now_utc).total_seconds()


async def run_daily_report_scheduler(bot: Bot) -> None:
    if ADMIN_TELEGRAM_ID is None:
        logger.warning(
            "ADMIN_TELEGRAM_ID no está configurado, el reporte diario automático queda desactivado"
        )
        return

    while True:
        wait_seconds = _seconds_until_next_report(datetime.now(timezone.utc))
        await asyncio.sleep(wait_seconds)
        await send_daily_report(bot)
