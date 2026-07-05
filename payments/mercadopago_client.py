import asyncio

import mercadopago

from config.config import MP_ACCESS_TOKEN, SUBSCRIPTION_PRICE_MXN, WEBHOOK_BASE_URL

sdk = mercadopago.SDK(MP_ACCESS_TOKEN)


def _create_preference_sync(user_id: int) -> dict:
    preference_data = {
        "items": [
            {
                "title": "Suscripción mensual - Canal premium",
                "quantity": 1,
                "unit_price": SUBSCRIPTION_PRICE_MXN,
                "currency_id": "MXN",
            }
        ],
        "external_reference": str(user_id),
        "notification_url": f"{WEBHOOK_BASE_URL}/webhook/mercadopago",
    }
    result = sdk.preference().create(preference_data)
    return result["response"]


async def create_payment_preference(user_id: int) -> str:
    preference = await asyncio.to_thread(_create_preference_sync, user_id)
    return preference["init_point"]


def _get_payment_sync(payment_id: str) -> dict:
    result = sdk.payment().get(payment_id)
    return result["response"]


async def get_payment(payment_id: str) -> dict:
    return await asyncio.to_thread(_get_payment_sync, payment_id)
