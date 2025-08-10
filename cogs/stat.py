import logging
import os
from datetime import datetime

import discord
from discord.ext import commands

from database.query import get_daily_stats, get_all_time_stats

logger = logging.getLogger(__name__)


class Stat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    stat = discord.SlashCommandGroup(name="stat", guild_ids=[int(os.getenv("GUILD_ID"))])

    @stat.command()
    async def daily(self, ctx: discord.ApplicationContext):
        daily_stats = await get_daily_stats()

        desc = ""
        for i in daily_stats:
            if not i == "api":
                user = await self.bot.fetch_user(i)
                nick = user.name
            else:
                nick = "API"

            desc += f"{nick}: {daily_stats[i]}" + "\n"

        embed = discord.Embed(
            title=f"Daily telegrams sent",
            description=desc,
            color=discord.Colour.blurple(),
        )

        embed.timestamp = datetime.now()

        await ctx.respond(embed=embed)

    @stat.command()
    async def total(self, ctx: discord.ApplicationContext):
        total_stats = await get_all_time_stats()

        desc = ""
        for i in total_stats:
            if not i == "api":
                user = await self.bot.fetch_user(i)
                nick = user.name
            else:
                nick = "API"
            desc += f"{nick}: {total_stats[i]}" + "\n"

        embed = discord.Embed(
            title=f"Total telegrams sent",
            description=desc,
            color=discord.Colour.blurple(),
        )

        embed.timestamp = datetime.now()

        await ctx.respond(embed=embed)


def setup(bot):
    logger.info("Loading statistics cog")
    bot.add_cog(Stat(bot))
