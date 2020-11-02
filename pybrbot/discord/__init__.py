import asyncio
import logging
import os
from collections import defaultdict
from typing import Optional

import discord
from loguru import logger
from discord.ext import commands
from discord.ext.tasks import loop
from slugify import slugify
from . import config, messages, utils
from .utils import cmdlog


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
invite_tracker = utils.InviteTracker(bot)
voice_channel_tracker = utils.VoiceChannelTracker()

TALK_CHANNELS = {
    "channel_pep0": "trilha-pep0",
    "channel_pep8": "trilha-pep8",
    "channel_pep20": "trilha-pep20",
    "channel_pep404": "trilha-pep404",
}


async def send_dm_member(member, message):
    logger.info(f"Sending welcome message. member={member.display_name!r}")
    await member.create_dm()
    await member.dm_channel.send(message)


async def welcome_member(member, guild):
    channels = {
        "channel_help": "ajuda",
        "channel_announcements": "anuncios",
    }
    channels.update(TALK_CHANNELS)
    channe_mentions = {
        key: discord.utils.get(guild.channels, name=name).mention
        for key, name in channels.items()
    }

    message = messages.WELCOME.format(
        name=member.name,
        **channe_mentions,
    )
    await send_dm_member(member, message)


async def welcome_speaker(member, guild):
    channels = {
        "channel_speakers": "ajuda-palestrantes",
        "channel_announcements": "anuncios",
    }
    channels.update(TALK_CHANNELS)
    channe_mentions = {
        key: discord.utils.get(guild.channels, name=name).mention
        for key, name in channels.items()
    }

    message = messages.WELCOME_SPEAKER.format(
        name=member.name,
        **channe_mentions,
    )
    await send_dm_member(member, message)


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
async def on_voice_state_update(member, before, after):
    channel = before.channel or after.channel

    if not channel or channel.category.name != "boteco":
        return

    global voice_channels_cache
    if len(channel.members) == 0:
        logger.info(f"Channel to be removed. channel={channel.name!r}")
        voice_channel_tracker.track(channel)

    if len(channel.members) > 0:
        voice_channel_tracker.stop_tracking(channel)


@bot.event
async def on_error(event, *args, **kwargs):
    """Don't ignore the error, causing Sentry to capture it."""
    raise


@bot.command()
@cmdlog
async def cdc(ctx, *args):
    role = utils.get_role(ctx.guild, "codigo-de-conduta")
    message = await ctx.channel.send(role.mention)

    cdc_channel = discord.utils.get(ctx.guild.channels, name="cdc")
    await cdc_channel.send(
        f"🚨 **Atenção!**\nAlerta enviado pela pessoa: {ctx.message.author.mention}\nLink para mensagem: {message.jump_url}"
    )
    await ctx.message.delete()


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
async def pep0_prox(ctx, *args):
    pep0_channel = discord.utils.get(ctx.guild.channels, name="trilha-pep0")
    await pep0_channel.send(messages.TALK.format(youtube_link=args[0] if args else ""))


@bot.command()
@cmdlog
async def pep8_prox(ctx, *args):
    pep8_channel = discord.utils.get(ctx.guild.channels, name="trilha-pep8")
    await pep8_channel.send(messages.TALK.format(youtube_link=args[0] if args else ""))


@bot.command()
@cmdlog
async def pep20_prox(ctx, *args):
    pep20_channel = discord.utils.get(ctx.guild.channels, name="trilha-pep20")
    await pep20_channel.send(messages.TALK.format(youtube_link=args[0] if args else ""))


@bot.command()
@cmdlog
async def pep404_prox(ctx, *args):
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
async def mesa(ctx, *args):
    boteco = discord.utils.get(ctx.guild.categories, name="boteco")
    tables = [table.name for table in boteco.voice_channels]

    if not args:
        logger.warning("missing table name!")
        await ctx.channel.send(
            "Opa, faltou dar um nome para a sua mesa, tente algo como `!mesa vim melhor que emacs` hahaha 😅"
        )
        return

    new_table = slugify("mesa " + " ".join(args))
    if new_table in tables:
        logger.warning(
            "This table already exists. new_table={new_table!r}, tables={tables!r}"
        )
        await ctx.channel.send(
            "Opa, uma mesa já existe com esse nome, mas sinta-se à vontade e participe da conversa! 😄 🍺"
        )
        return

    channel = await boteco.create_voice_channel(new_table, user_limit=10)
    voice_channel_tracker.track(channel)
    await ctx.message.add_reaction("🍻")
    await ctx.channel.send(f"Mesa disponível no **#boteco**")


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


@loop(minutes=1)
async def close_empty_tables():
    if len(voice_channel_tracker) == 0:
        return

    logger.info("Running job: close_empty_tables")
    await voice_channel_tracker.delete_empty_channels()
