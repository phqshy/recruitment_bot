import asyncio
import json
import logging
import pickle
import signal
import sys
from collections import deque
from pathlib import Path

founded_stack = deque(maxlen=1000)
nations_lock = asyncio.Lock()

logger = logging.getLogger(__name__)


async def add_nation(nation: str) -> None:
    async with nations_lock:
        founded_stack.append(nation)
        logger.debug(f"Added {nation} to queue")


async def get_manual_nations() -> list[str] | None:
    async with nations_lock:
        if len(founded_stack) == 0:
            return None

        nation = []
        for i in range(min(8, len(founded_stack))):
            nation.append(founded_stack.pop())

        return nation


async def get_single_nation() -> str | None:
    async with nations_lock:
        if len(founded_stack) == 0:
            return None
        return founded_stack.pop()


async def prune_queue(new_size: int) -> None:
    async with nations_lock:
        while len(founded_stack) > new_size:
            founded_stack.popleft()


async def get_queue_length() -> int:
    async with nations_lock:
        return len(founded_stack)


def dump_and_exit(sig, frame) -> None:
    pickle.dump(founded_stack, open("queue.dump", "wb"))
    logger.info("Wrote queue to file")
    logger.info("Exiting program")
    sys.exit()


file = Path("queue.dump")
if file.is_file():
    founded_stack = pickle.load(open("queue.dump", "rb"))

signal.signal(signal.SIGINT, dump_and_exit)
logger.info("Initialized nation queue")
