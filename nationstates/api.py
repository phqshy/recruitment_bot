import asyncio
import logging
import os
import signal
from datetime import datetime

import sans

from database.query import log_telegram
from nationstates.nation_queue import get_single_nation

logger = logging.getLogger(__name__)


async def api_coroutine():
    limiter = sans.TelegramLimiter(recruitment=True)
    secret_key = os.getenv("SECRET_KEY")
    telegram_id = os.getenv("TELEGRAM_ID")
    api_key = os.getenv("API_KEY")

    try:
        while True:
            try:
                next_nation = await get_single_nation()

                if next_nation is not None:
                    # send telegram
                    sans.get(sans.Telegram(api_key, telegram_id, secret_key, next_nation), auth=limiter)
                    logger.debug(f"Telegram sent to {next_nation}")

                    # log sent telegram
                    await log_telegram("api", next_nation, "tgid", datetime.now())
            except Exception:
                logger.warning("Python exception occurred in API loop.")
                pass

            await asyncio.sleep(3 * 60)
    except Exception:
        logger.error("Fatal error in API loop! Exiting program...")
        signal.raise_signal(signal.SIGINT)
