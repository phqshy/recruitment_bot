import asyncio
import logging
import re

import sans
from httpx import ReadError

from nationstates.nation_queue import add_nation

numbers = "1234567890"

logger = logging.getLogger(__name__)


async def founding_listener():
    async with sans.AsyncClient() as client:
        async for event in sans.serversent_events(client, "founding"):
            regex_match = re.search("@@(.+)@@", event['str'])
            if regex_match is not None:
                nation = regex_match.group().replace("@", "")
                should_add = True

                for i in numbers:
                    if i in nation:
                        should_add = False
                        break

                if should_add:
                    await add_nation(nation)


async def sse_coroutine():
    sans.set_agent("The Yeetusa (the.yeetusa@gmail.com)")

    while True:
        try:
            await founding_listener()
        except ReadError:
            logger.warning("SSE error, rebooting listener!")
