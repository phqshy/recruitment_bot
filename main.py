import asyncio
import logging
import os

import nest_asyncio
from dotenv import load_dotenv

from bot import discord_bot
from nationstates.api import api_coroutine
from nationstates.foundings_sse import sse_coroutine

nest_asyncio.apply()
load_dotenv()
logging.basicConfig(level=logging.INFO)


async def main():
    await asyncio.gather(
        discord_bot.start(os.getenv("TOKEN")),
        api_coroutine(),
        sse_coroutine()
    )


if __name__ == "__main__":
    asyncio.run(main())
