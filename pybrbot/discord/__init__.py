import logging
import os
from collections import defaultdict
from typing import Optional

import discord
from loguru import logger
from discord.ext import commands
from . import config, messages, utils


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
invite_tracker = utils.InviteTracker(bot)

TALK_CHANNELS = {
    "channel_pep0": "trilha-pep0",
    "channel_pep8": "trilha-pep8",
    "channel_pep20": "trilha-pep20",
    "channel_pep404": "trilha-pep404",
}



async def send_dm_member(member, message):
    logger.info(f"Sending welcome message. member={member.display_name}")
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
        "channel_speakers": "palestrantes",
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

    logger.info(f'{bot.user} has connected to Discord!\n')
    for guild in bot.guilds:
        print(guild.name, guild.id)
        for role in guild.roles:
            print(f"  {role.name}: {role.id}")

        print()


@bot.event
async def on_member_join(member):
    logger.info(f"New member joined. member={member.display_name}")

    new_role = await invite_tracker.check_member_role(member)
    logger.info(f"Role updated. member={member.display_name!r}, new_role={new_role.id!r}, speaker_role={utils.SPEAKER_ROLE!r}")

    if new_role and new_role.id == utils.SPEAKER_ROLE:
        await welcome_speaker(member, member.guild)
    else:
        await welcome_member(member, member.guild)


@bot.command()
async def welcome(ctx):
    member = ctx.message.author
    logger.info(f"!welcome command trigger by member. member={member}, type={type}")
    await welcome_member(member, ctx.guild)
    await welcome_speaker(member, ctx.guild)


@bot.command()
async def channel(ctx, *args):
    logger.info(f"!channel command trigger by member. member={ctx.message.author}")

    message = f"Guild: {ctx.message.guild}\n"
    message += "Channels:\n"
    for channel in ctx.message.guild.channels:
        message += f"- {channel.name} {channel.mention}\n"

    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(message)


@bot.command()
async def invites(ctx, *args):
    logger.info(f"!invites command trigger by member. member={ctx.message.author!r}")

    roles = ctx.message.guild.roles
    message = "Códigos de convite:\n"
    for code, role_id in invite_tracker.invite_roles.items():
        role_mention = discord.utils.get(ctx.message.guild.roles, id=role_id).mention
        message += f"{role_mention} <https://discord.gg/{code}>\n"

    await ctx.channel.send(message)

@bot.command()
async def cdc(ctx, *args):
    logger.info(f"/cdc command trigger by member. member={ctx.message.author}")
    role = utils.get_role(ctx.guild, "codigo-de-conduta")
    await ctx.channel.send(role.mention)

    cdc_channel = discord.utils.get(ctx.guild.channels, name="cdc")
    await cdc_channel.send(f"🚨 Atenção! Link: {ctx.message.jump_url}")
