import asyncio

import aiosqlite


async def setup_database():
    async with aiosqlite.connect("recruitment.db") as con:
        await con.execute("CREATE TABLE IF NOT EXISTS telegrams"
                          "(source TEXT, target TEXT, content TEXT, timestamp INTEGER)")
        await con.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, nation TEXT, template TEXT)")
        await con.commit()

