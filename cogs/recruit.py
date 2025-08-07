import asyncio
import datetime
import logging
from typing import Optional

import discord
from discord.ext import commands

from database.query import register_user, lookup_user, log_telegram, update_user
from nationstates.nation_queue import get_manual_nations, prune_queue, get_queue_length

open_sessions = {}

logger = logging.getLogger(__name__)


class UrlButton(discord.ui.Button):
    def __init__(self, nations, template, user):
        super().__init__(label="Open nations",
                         url=f'https://www.nationstates.net/page=compose_telegram?tgto={",".join(nations)}'
                             f'&message={template}&script=Blue_Ridge_Recruiting__by_The_Yeetusa__usedBy_{user}'
                             f'&userclick={datetime.datetime.now().timestamp()}')


class TelegramButtonView(discord.ui.View):
    def __init__(self, nations, template, user):
        super().__init__(timeout=None)

        url_button = UrlButton(nations, template, user)
        self.add_item(url_button)


def generate_recruitment_embed(nations: list[str]):
    desc = '\n'.join(nations)

    embed = discord.Embed(
        title="Manual recruitment batch",
        description=desc,
        color=discord.Colour.blurple(),
    )

    return embed


async def run_session(bot: discord.Bot, channel_id, user_id, nation, template, sleep=40):
    while user_id in open_sessions:
        nations = await get_manual_nations()

        if nations is not None:
            time = datetime.datetime.now()

            for i in nations:
                await log_telegram(user_id, i, template, time)

            view = TelegramButtonView(nations, template, nation)
            await bot.get_channel(channel_id).send(f"<@!{user_id}>",
                                                   embed=generate_recruitment_embed(nations), view=view)
        await asyncio.sleep(sleep)


class Recruit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    recruit = discord.SlashCommandGroup(name="recruit", guild_ids=[904135949900976159])

    @recruit.command(description="Opens a new recruitment session")
    @discord.option("delay", description="Recruitment delay (default 40s)",
                    type=discord.SlashCommandOptionType.integer, required=False)
    async def open_session(self, ctx: discord.ApplicationContext, delay: int | None):
        loop = asyncio.get_event_loop()
        open_sessions[ctx.author.id] = True

        data, telegrams = await lookup_user(ctx.author.id)

        if data is None:
            embed = discord.Embed(
                title=f"Failed to open session: recruiter not found",
                description="Run `/recruit register_recruiter` in order to begin recruiting.",
                color=discord.Colour.blurple(),
            )

            await ctx.respond(embed=embed)
            return

        embed = discord.Embed(
            title=f"Opening recruitment session for {ctx.author.display_name}",
            color=discord.Colour.blurple(),
        )

        embed.timestamp = datetime.datetime.now()

        await ctx.respond(embed=embed)

        if delay is None:
            delay = 40

        task = loop.create_task(run_session(self.bot, ctx.channel_id, ctx.author.id, data[1], data[2], sleep=delay))
        loop.run_until_complete(task)

    @recruit.command(description="Closes a recruitment session")
    @discord.option("user", description="The user to close a session for",
                    type=discord.SlashCommandOptionType.user, required=False)
    async def close_session(self, ctx: discord.ApplicationContext, user: discord.User | None):
        if user is None:
            user = ctx.user

        if user.id not in open_sessions:
            embed = discord.Embed(
                title=f"No open session found",
                color=discord.Colour.blurple(),
            )

            await ctx.respond(embed=embed)
            return

        del open_sessions[user.id]

        embed = discord.Embed(
            title=f"Closing session for {user.display_name}",
            color=discord.Colour.blurple(),
        )

        embed.timestamp = datetime.datetime.now()

        await ctx.respond(embed=embed)

    @recruit.command(description="Register a new recruiter with the system")
    @discord.option("nation", description="Your nation name", type=discord.SlashCommandOptionType.string)
    @discord.option("template", description="Your telegram template", type=discord.SlashCommandOptionType.string)
    async def register_recruiter(self, ctx: discord.ApplicationContext, nation: str, template: str):
        await register_user(ctx.author.id, nation, template)
        desc = f"User: {ctx.author.display_name}" + "\n" + f"Nation: {nation}" + "\n" + f"Telegram template: {template}"

        embed = discord.Embed(
            title=f"Registered new recruiter",
            description=desc,
            color=discord.Colour.blurple(),
        )

        embed.timestamp = datetime.datetime.now()

        await ctx.respond(embed=embed)

    @recruit.command(description="Get a recruiter's data")
    @discord.option("user", description="User to look up",
                    type=discord.SlashCommandOptionType.user, required=False)
    async def lookup_recruiter(self, ctx: discord.ApplicationContext, user: Optional[discord.User]):
        data, telegrams_sent = await lookup_user(ctx.author.id if user is None else user.id)

        desc = f"Telegram template: {data[2]}" + "\n" + f"Telegrams sent: {telegrams_sent}"

        embed = discord.Embed(
            title=f"Recruiter report for " + data[1],
            description=desc,
            color=discord.Colour.blurple(),
        )

        embed.timestamp = datetime.datetime.now()

        await ctx.respond(embed=embed)

    @recruit.command(description="Change your nation or telegram template")
    @discord.option("template", type=discord.SlashCommandOptionType.string, required=False)
    @discord.option("nation", type=discord.SlashCommandOptionType.string, required=False)
    async def update_recruiter(self, ctx: discord.ApplicationContext, template: Optional[str], nation: Optional[str]):
        await update_user(ctx.author.id, telegram_template=template, nation=nation)

        embed = discord.Embed(
            title=f"Updated recruiter",
            color=discord.Colour.blurple(),
        )

        embed.timestamp = datetime.datetime.now()

        await ctx.respond(embed=embed)

    @recruit.command(description="Get the length of the current global queue")
    @discord.option("prune", description="Prunes the queue to the given length",
                    type=discord.SlashCommandOptionType.integer, required=False)
    async def queue_size(self, ctx: discord.ApplicationContext, prune: Optional[int]):
        if prune is not None:
            await prune_queue(prune)

        queue_length = await get_queue_length()

        embed = discord.Embed(
            title=f"Queue length is currently {queue_length}",
            color=discord.Colour.blurple(),
        )

        embed.timestamp = datetime.datetime.now()

        await ctx.respond(embed=embed)


def setup(bot):
    logger.info("Loading recruitment cog")
    bot.add_cog(Recruit(bot))
