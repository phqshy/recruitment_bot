import logging

import discord

from database.setup import setup_database

discord_bot = discord.Bot()

discord_bot.load_extension("cogs.recruit")
discord_bot.load_extension("cogs.stat")

logger = logging.getLogger(__name__)


@discord_bot.event
async def on_ready():
    await setup_database()
    logger.info(f"Logged in as {discord_bot.user}")


@discord_bot.slash_command(name="ping", description="Ping the bot", guild_ids=[842498286920269844])
async def ping_command(ctx: discord.ApplicationContext):
    await ctx.respond(f"Pong! Latency is {round(discord_bot.latency * 1000, 2)}ms")

