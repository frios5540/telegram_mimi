import sqlite3
from datetime import datetime, timedelta

import aiosqlite

from database.db import DB_PATH


async def upsert_subscription(
    user_id: int, payment_id: str, paid_at: datetime, expires_at: datetime
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO subscriptions (user_id, payment_id, paid_at, expires_at, status)
            VALUES (?, ?, ?, ?, 'active')
            ON CONFLICT(user_id) DO UPDATE SET
                payment_id = excluded.payment_id,
                paid_at = excluded.paid_at,
                expires_at = excluded.expires_at,
                status = 'active',
                renewal_reminder_sent_at = NULL
            """,
            (user_id, payment_id, paid_at.isoformat(), expires_at.isoformat()),
        )
        await db.commit()


async def payment_already_processed(payment_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM subscriptions WHERE payment_id = ?", (payment_id,)
        )
        row = await cursor.fetchone()
        return row is not None


async def get_subscription(user_id: int) -> sqlite3.Row | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        cursor = await db.execute(
            "SELECT * FROM subscriptions WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone()


async def get_expired_subscriptions(now: datetime) -> list[sqlite3.Row]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        cursor = await db.execute(
            "SELECT * FROM subscriptions WHERE status = 'active' AND expires_at < ?",
            (now.isoformat(),),
        )
        return await cursor.fetchall()


async def mark_expired(user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE subscriptions SET status = 'expired' WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()


async def get_subscriptions_due_for_reminder(now: datetime) -> list[sqlite3.Row]:
    window_end = now + timedelta(hours=24)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        cursor = await db.execute(
            """
            SELECT * FROM subscriptions
            WHERE status = 'active'
              AND expires_at BETWEEN ? AND ?
              AND renewal_reminder_sent_at IS NULL
            """,
            (now.isoformat(), window_end.isoformat()),
        )
        return await cursor.fetchall()


async def mark_reminder_sent(user_id: int, sent_at: datetime) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE subscriptions SET renewal_reminder_sent_at = ? WHERE user_id = ?",
            (sent_at.isoformat(), user_id),
        )
        await db.commit()
