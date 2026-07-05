# Telegram Premium Bot

Bot de Telegram construido con [aiogram](https://docs.aiogram.dev/) 3.x.

## Estructura del proyecto

```
telegram-premium/
├── config/       # Configuración y variables de entorno
├── database/     # Acceso a la base de datos SQLite (suscripciones)
├── handlers/     # Handlers de comandos y mensajes
├── payments/     # Integración con Mercado Pago (preferencias y webhook)
├── services/     # Lógica de negocio (expiración de suscripciones)
├── utils/        # Utilidades compartidas (logging, helpers, etc.)
├── main.py       # Punto de entrada: bot + servidor webhook + checker
└── requirements.txt
```

## Instalación

1. Crea y activa un entorno virtual:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Copia `.env.example` a `.env` y coloca tu token de bot:

   ```bash
   cp .env.example .env
   ```

   Edita `.env`:

   ```
   BOT_TOKEN=tu_token_de_botfather
   CHANNEL_ID=-1001234567890
   MP_ACCESS_TOKEN=tu_access_token_de_mercado_pago
   MP_WEBHOOK_SECRET=tu_clave_secreta_de_webhooks
   WEBHOOK_BASE_URL=https://tu-app.onrender.com
   SUBSCRIPTION_PRICE_MXN=450
   PORT=8080
   ```

## Ejecución

```bash
python main.py
```

## Comandos disponibles

- `/start`: Mensaje de bienvenida al canal premium.
- `/suscribirme`: Genera un link de pago de Mercado Pago (450 MXN/mes) y lo envía al usuario.

## Obtener el CHANNEL_ID de tu canal privado

El bot incluye un handler ([handlers/channel_info.py](handlers/channel_info.py)) que detecta y registra en consola el ID de cualquier canal donde reciba una publicación.

Pasos:

1. Agrega tu bot como **administrador** de tu canal privado (Telegram no permite agregar bots como miembros normales de un canal, deben ser admins). No necesita permisos especiales, con cualquier rol de administrador basta.
2. Ejecuta el bot: `python main.py`.
3. Publica cualquier mensaje en el canal (puede ser de prueba, luego lo puedes borrar).
4. Revisa la consola donde corre el bot. Verás un log como:

   ```
   INFO - handlers.channel_info - Canal detectado -> título: Mi Canal Premium | ID: -1001234567890
   ```

5. Copia ese ID (incluyendo el signo `-`) y colócalo en tu `.env`:

   ```
   CHANNEL_ID=-1001234567890
   ```

Una vez que tengas el `CHANNEL_ID` guardado, ya está disponible en `config/config.py` para usarlo en la lógica futura del bot (por ejemplo, para invitar usuarios o verificar membresías).

## Sistema de pagos con Mercado Pago

El flujo es: el usuario ejecuta `/suscribirme` → paga 450 MXN en Mercado Pago → Mercado Pago notifica al bot por webhook → el bot verifica el pago, lo guarda en SQLite y manda un link de invitación de un solo uso, válido 24 horas → pasados 30 días desde el pago, un checker en segundo plano expulsa al usuario del canal automáticamente.

### 1. Obtener las credenciales de Mercado Pago

1. Entra al [panel de desarrolladores de Mercado Pago](https://www.mercadopago.com.mx/developers/panel) con tu cuenta.
2. Crea o selecciona tu aplicación y copia el **Access Token** (usa el de prueba mientras desarrollas, y el de producción cuando cobres de verdad). Va en `MP_ACCESS_TOKEN`.
3. En la misma aplicación, ve a **Webhooks → Configurar notificaciones**, activa el tema **Pagos** y copia la **clave secreta** que se genera ahí. Va en `MP_WEBHOOK_SECRET`. Esta clave es la que el bot usa para verificar que las notificaciones realmente vienen de Mercado Pago (header `x-signature`) y no de un tercero.

### 2. Exponer el webhook (`WEBHOOK_BASE_URL`)

Mercado Pago necesita poder golpear tu servidor por HTTPS, así que `WEBHOOK_BASE_URL` debe ser una URL pública:

- **En producción (Render)**: despliega este proyecto como un *Web Service* (no como *Background Worker*), porque el bot expone un servidor HTTP en el puerto de la variable `PORT` (Render la inyecta automáticamente) para recibir el webhook. Usa la URL que Render te asigne, por ejemplo `https://telegram-premium.onrender.com`.
- **En local, para probar**: usa un túnel como [ngrok](https://ngrok.com/) (`ngrok http 8080`) y pon la URL que te da (`https://xxxx.ngrok-free.app`) en `WEBHOOK_BASE_URL`.

> ⚠️ **Nota sobre SQLite en Render**: la base de datos vive en un archivo (`database/subscriptions.db`) en el disco del servicio. En el plan gratuito/estándar de Render el disco es efímero: se borra en cada redeploy o reinicio. Si vas en serio con esto en producción, considera agregar un [Persistent Disk](https://render.com/docs/disks) de Render, o migrar a PostgreSQL más adelante.

### 3. Probar el flujo completo

1. Corre `python main.py`. Debe iniciar el bot (polling), el servidor webhook en `PORT`, y crear `database/subscriptions.db` con la tabla `subscriptions`.
2. En Telegram, manda `/suscribirme` al bot. Te debe responder con un botón "💳 Pagar ahora" que abre el checkout de Mercado Pago.
3. Paga con una [tarjeta de prueba de Mercado Pago](https://www.mercadopago.com.mx/developers/es/docs/checkout-pro/additional-content/your-integrations/test/cards) si estás en modo sandbox.
4. Al aprobarse el pago, Mercado Pago llama a `WEBHOOK_BASE_URL/webhook/mercadopago`. El bot valida la firma, confirma el pago contra la API de Mercado Pago, guarda la suscripción (30 días desde el pago) y te manda el link de invitación de un solo uso por chat privado.
5. Pasados 30 días (o si adelantas manualmente la fecha `expires_at` en `database/subscriptions.db` para probar), el checker en segundo plano (corre cada hora) expulsa al usuario del canal y marca la suscripción como `expired`.
