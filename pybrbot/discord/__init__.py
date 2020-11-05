import asyncio
import logging
import os
from collections import defaultdict
from typing import Optional

import discord
from loguru import logger
from discord.ext.commands import Bot
from discord.ext.tasks import loop
from slugify import slugify
from . import calendar, config, messages, utils
from .commands import Commands
from .utils import cmdlog


bot = Bot(command_prefix="!", intents=discord.Intents.all())
bot.add_cog(Commands(bot))
invite_tracker = utils.InviteTracker(bot)

TALK_CHANNELS = {
    "channel_pep0": "trilha-pep0",
    "channel_pep8": "trilha-pep8",
    "channel_pep20": "trilha-pep20",
    "channel_pep404": "trilha-pep404",
}

CHANNEL_ROOMS = [
    {
        "discord_channel": "trilha-pep{}".format(pep_number),
        "calendar_room_name": "PEP {}".format(pep_number),
    }
    for pep_number in [0, 8, 20, 404]
]


@bot.event
async def on_ready():
    await invite_tracker.sync()

    logger.info(f"{bot.user!r} has connected to Discord!\n")
    for guild in bot.guilds:
        print(guild.name, guild.id)
        for role in guild.roles:
            print(f"  {role.name}: {role.id}")

        print()


@bot.event
async def on_message(message):
    if not message.author.bot and message.content.lower() == "galvão?":
        await message.channel.send("Fala Tino!")

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    logger.info(f"New member joined. member={member.display_name!r}")

    new_role = await invite_tracker.check_member_role(member)
    new_role_id = getattr(new_role, "id", None)
    logger.info(
        f"Role updated. member={member.display_name!r}, new_role={new_role_id!r}, speaker_role={utils.SPEAKER_ROLE!r}"
    )


@bot.event
async def on_error(event, *args, **kwargs):
    """Don't ignore the error, causing Sentry to capture it."""
    raise


@bot.command()
@cmdlog
async def geral(ctx, *args):
    geral_channel = discord.utils.get(ctx.guild.channels, name="geral")
    await geral_channel.send(messages.GERAL)


@bot.command()
@cmdlog
async def anuncio(ctx, *args):
    anuncios_channel = discord.utils.get(ctx.guild.channels, name="anuncios")
    await anuncios_channel.send(messages.WARNING.format(warning_text=" ".join(args)))


@bot.command()
@cmdlog
async def pep0_prox_backup(ctx, *args):
    pep0_channel = discord.utils.get(ctx.guild.channels, name="trilha-pep0")
    await pep0_channel.send(messages.TALK.format(youtube_link=args[0] if args else ""))


@bot.command()
@cmdlog
async def pep8_prox_backup(ctx, *args):
    pep8_channel = discord.utils.get(ctx.guild.channels, name="trilha-pep8")
    await pep8_channel.send(messages.TALK.format(youtube_link=args[0] if args else ""))


@bot.command()
@cmdlog
async def pep20_prox_backup(ctx, *args):
    pep20_channel = discord.utils.get(ctx.guild.channels, name="trilha-pep20")
    await pep20_channel.send(messages.TALK.format(youtube_link=args[0] if args else ""))


@bot.command()
@cmdlog
async def pep404_prox_backup(ctx, *args):
    pep404_channel = discord.utils.get(ctx.guild.channels, name="trilha-pep404")
    await pep404_channel.send(
        messages.TALK.format(youtube_link=args[0] if args else "")
    )


@bot.command()
@cmdlog
async def welcome_boteco(ctx, *args):
    channel_name = "peca-uma-mesa" if len(args) == 0 else args[0]
    boteco = discord.utils.get(ctx.guild.channels, name=channel_name)
    channel_help = discord.utils.get(ctx.guild.channels, name="ajuda").mention
    await boteco.send(messages.BOTECO_WELCOME.format(channel_help=channel_help))


@bot.command()
@cmdlog
async def msg(ctx, *args):
    if len(args) < 2:
        logger.warning("missing destination message and message")
        await ctx.channel.send("!msg #canal mensagem a ser enviada")
        return

    if args[0].startswith("<#"):
        channel_id = int(args[0][2:-1])
        destination = discord.utils.get(ctx.guild.channels, id=channel_id)
    elif args[0].startswith("<@"):
        member_id = int(args[0][2:-1])
        destination = discord.utils.get(ctx.guild.members, id=member_id)
    else:
        logger.warning(f"Not a channel or user. args={args}")
        await ctx.channel.send(
            f"Uhmm, não encontrei o canal/membro **{args[0]}** para enviar a mensagem"
        )
        return

    if not destination:
        logger.warning(
            f"Destination not found. destination={destination!r}, args={args!r}"
        )
        return

    message = " ".join(args[1:])
    logger.info(f"message sent. destination={destination}, message={message}")
    await destination.send(message)


@bot.command()
@cmdlog
async def alerta_palestras(ctx, *args):
    guild = await bot.fetch_guild(config.GUILD)
    channels = await guild.fetch_channels()

    events = calendar.fetch_events()

    announcement = {}
    for room in CHANNEL_ROOMS:
        discord_channel = room["discord_channel"]
        room_name = room["calendar_room_name"]
        pep = room_name.replace(" ", "").lower()

        event = calendar.next_event(events, room_name)
        room = discord.utils.get(channels, name=discord_channel)

        title = event["summary"]
        youtube = event["extendedProperties"]["private"]["youtube_channel"]

        await room.send(
            messages.NEXT_TALK.format(
                talk_title=title,
                talk_description=event.get("description"),
                youtube_url=youtube,
            )
        )

        announcement[f"{pep}_channel"] = room.mention
        announcement[f"{pep}_youtube"] = youtube
        announcement[f"{pep}_title"] = title

    general = discord.utils.get(channels, name="geral")
    await general.send(messages.NEXT_TALK_ALL.format(**announcement))
