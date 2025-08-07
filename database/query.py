import datetime
import time

import aiosqlite


async def log_telegram(source, target, content, timestamp):
    async with aiosqlite.connect("recruitment.db") as con:
        await con.execute("INSERT INTO telegrams VALUES (?, ?, ?, ?)", (source, target, content, timestamp))
        await con.commit()


async def register_user(discord_id, nation, telegram_template):
    async with aiosqlite.connect("recruitment.db") as con:
        await con.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
                          (discord_id, normalize(nation), telegram_template))
        await con.commit()


async def lookup_user(discord_id):
    async with aiosqlite.connect("recruitment.db") as con:
        cur = await con.cursor()
        await cur.execute("SELECT * FROM users WHERE id = ?", (discord_id,))

        user_row = await cur.fetchone()
        await cur.close()

        if user_row is None:
            return None

        cur = await con.cursor()
        await cur.execute("SELECT * FROM telegrams WHERE source = ?", (discord_id,))
        results = await map_telegram_rows(cur)
        await cur.close()

        return user_row, results[discord_id] if discord_id in results else 0


async def update_user(discord_id, nation=None, telegram_template=None):
    async with aiosqlite.connect("recruitment.db") as con:
        if nation is not None:
            await con.execute("UPDATE users SET nation = ? WHERE id = ?",
                              (normalize(nation), discord_id))

        if telegram_template is not None:
            await con.execute("UPDATE users SET template = ? WHERE id = ?",
                              (telegram_template, discord_id))
        await con.commit()


async def get_daily_stats():
    async with aiosqlite.connect("recruitment.db") as con:
        timestamp = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
        cur = await con.cursor()
        await cur.execute("SELECT * FROM telegrams WHERE timestamp > ?", (timestamp,))

        results = await map_telegram_rows(cur)
        await cur.close()
        return results


async def get_all_time_stats():
    async with aiosqlite.connect("recruitment.db") as con:
        cur = await con.cursor()
        await cur.execute("SELECT * FROM telegrams")

        results = await map_telegram_rows(cur)
        await cur.close()
        return results


def normalize(nation: str):
    return nation.strip().replace(" ", "_").lower()


async def map_telegram_rows(cursor):
    results = {}
    for i in await cursor.fetchall():
        source = i[0]
        if source in results:
            results[source] += 1
        else:
            results[source] = 1
    return results
