import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiohttp import web

from config.config import CHANNEL_ID, MP_WEBHOOK_SECRET
from database.subscriptions import payment_already_processed, upsert_subscription
from payments.mercadopago_client import get_payment

logger = logging.getLogger(__name__)


def _verify_signature(request: web.Request, data_id: str) -> bool:
    x_signature = request.headers.get("x-signature", "")
    x_request_id = request.headers.get("x-request-id", "")

    parts = dict(part.split("=", 1) for part in x_signature.split(",") if "=" in part)
    ts = parts.get("ts")
    v1 = parts.get("v1")
    if not ts or not v1:
        return False

    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
    computed = hmac.new(
        MP_WEBHOOK_SECRET.encode(), manifest.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed, v1)


async def _get_data_id(request: web.Request) -> str | None:
    data_id = request.query.get("data.id")
    if data_id:
        return data_id

    if request.can_read_body:
        body = await request.json()
        return str(body.get("data", {}).get("id", "")) or None

    return None


async def handle_mercadopago_webhook(request: web.Request) -> web.Response:
    data_id = await _get_data_id(request)
    if not data_id:
        return web.Response(status=400)

    if not _verify_signature(request, data_id):
        logger.warning("Firma inválida en webhook de Mercado Pago")
        return web.Response(status=401)

    payment = await get_payment(data_id)

    if payment.get("status") != "approved":
        return web.Response(status=200)

    payment_id = str(payment["id"])
    if await payment_already_processed(payment_id):
        return web.Response(status=200)

    user_id = int(payment["external_reference"])
    paid_at = datetime.now(timezone.utc)
    expires_at = paid_at + timedelta(days=30)
    await upsert_subscription(user_id, payment_id, paid_at, expires_at)

    bot: Bot = request.app["bot"]
    invite_link = await bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        member_limit=1,
        expire_date=paid_at + timedelta(hours=24),
    )
    await bot.send_message(
        user_id,
        "¡Pago confirmado! Aquí está tu acceso de un solo uso al canal premium:\n"
        f"{invite_link.invite_link}\n\n"
        "Válido por 24 horas o hasta que lo uses, lo que ocurra primero.",
    )

    return web.Response(status=200)


def create_webhook_app(bot: Bot) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app.router.add_post("/webhook/mercadopago", handle_mercadopago_webhook)
    return app
