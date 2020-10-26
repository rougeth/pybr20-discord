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


async def send_dm_member(member, message):
    logger.info(f"Sending welcome message. member={member.display_name}")
    await member.create_dm()
    await member.dm_channel.send(message)

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
    
    role = utils.get_role(member.guild, "codigo-de-conduta")
    message = messages.WELCOME.format(
        name=member.name,
        cdc_team=role,
    )
    await invite_tracker.check_member_role(member)
    await send_dm_member(member, message)


@bot.command()
async def welcome(ctx):
    member = ctx.message.author
    logger.info(f"!welcome command trigger by member. member={member}, type={type}")

    cdc_team = utils.get_role(ctx.guild, "codigo-de-conduta")
    message = messages.WELCOME.format(
        name=member.name,
        cdc_team=cdc_team,
    )
    await send_dm_member(member, message)

    channels = ctx.guild.channels
    channel_speakers = discord.utils.get(channels, name="palestrantes").mention
    channel_announcements = discord.utils.get(channels, name="anuncios").mention
    channel_pep0 = discord.utils.get(channels, name="trilha-pep0").mention
    channel_pep8 = discord.utils.get(channels, name="trilha-pep8").mention
    channel_pep20 = discord.utils.get(channels, name="trilha-pep20").mention
    channel_pep404 = discord.utils.get(channels, name="trilha-pep404").mention

    message = messages.WELCOME_SPEAKER.format(
        name=member.name,
        channel_speakers=channel_speakers,
        channel_announcements=channel_announcements,
        channel_pep0=channel_pep0,
        channel_pep8=channel_pep8,
        channel_pep20=channel_pep20,
        channel_pep404=channel_pep404,
    )
    await send_dm_member(member, message)
        




@bot.command()
async def channel(ctx, *args):
    logger.info(f"!channel command trigger by member. member={ctx.message.author}")

    message = f"Guild: {ctx.message.guild}\n"
    message += "Channels:\n"
    for channel in ctx.message.guild.channels:
        message += f"- {channel.name} {channel.mention}"

    await ctx.message.author.create_dm()
    await ctx.message.author.dm_channel.send(message)


@bot.command()
async def cdc(ctx, *args):
    logger.info(f"/cdc command trigger by member. member={ctx.message.author}")
    role = utils.get_role(ctx.guild, "codigo-de-conduta")
    message = f"{role.mention} - https://python.org.br/cdc"
    await ctx.channel.send(messages.CDC.format(
        cdc_team=role.mention
    ))
