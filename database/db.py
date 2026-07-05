from pathlib import Path

import aiosqlite

DB_PATH = Path(__file__).parent / "subscriptions.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS subscriptions (
    user_id INTEGER PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    paid_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    renewal_reminder_sent_at TEXT
)
"""


async def _ensure_reminder_column(db: aiosqlite.Connection) -> None:
    cursor = await db.execute("PRAGMA table_info(subscriptions)")
    columns = [row[1] for row in await cursor.fetchall()]
    if "renewal_reminder_sent_at" not in columns:
        await db.execute(
            "ALTER TABLE subscriptions ADD COLUMN renewal_reminder_sent_at TEXT"
        )


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE_SQL)
        await _ensure_reminder_column(db)
        await db.commit()
