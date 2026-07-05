from pathlib import Path

import aiosqlite

DB_PATH = Path(__file__).parent / "subscriptions.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS subscriptions (
    user_id INTEGER PRIMARY KEY,
    payment_id TEXT UNIQUE NOT NULL,
    paid_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
)
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()
