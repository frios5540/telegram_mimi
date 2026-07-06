import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
MP_WEBHOOK_SECRET = os.getenv("MP_WEBHOOK_SECRET")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL")
SUBSCRIPTION_PRICE_MXN = float(os.getenv("SUBSCRIPTION_PRICE_MXN", "450"))
PORT = int(os.getenv("PORT", "8080"))
_admin_id_raw = os.getenv("ADMIN_TELEGRAM_ID")
ADMIN_TELEGRAM_ID = int(_admin_id_raw) if _admin_id_raw else None

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN no está definido. Revisa tu archivo .env")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID no está definido. Revisa tu archivo .env")

CHANNEL_ID = int(CHANNEL_ID)

# Las variables de Mercado Pago son opcionales: el bot debe poder arrancar
# (con /start funcionando) aunque los pagos todavía no estén configurados.
# Solo se necesitan cuando de verdad se usa /suscribirme o llega un webhook.

# ADMIN_TELEGRAM_ID también es opcional por la misma razón: si falta, el
# reporte diario simplemente no se envía y /reporte responde que no está
# configurado, en vez de tumbar todo el bot.
