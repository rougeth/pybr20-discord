# bot.py
import os
from collections import defaultdict

import discord
from discord.ext import commands
from . import config, messages, utils


intents = discord.Intents(members=True, guilds=True)
bot = commands.Bot(command_prefix="/")
invite_tracker = utils.InviteTracker(bot)


async def welcome_message(member):
    role = utils.get_role(member.guild, "codigo-de-conduta")
    await member.create_dm()
    await member.dm_channel.send(messages.WELCOME.format(
        name=member.name,
        cdc_team=role,
    ))

@bot.event
async def on_ready():
    await invite_tracker.sync()
    print(invite_tracker.diff())
    
    print(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        print(guild.name, guild.id)
        for role in guild.roles:
            print(role.name, role.id)
        
        print()


@bot.event
async def on_member_join(member):
    await invite_tracker.check_member_role(member)
    await welcome_message(member)


@bot.command()
async def welcome(ctx, *args):
    await welcome_message(ctx.message.author)


@bot.command()
async def cdc(ctx, *args):
    role = utils.get_role(ctx.guild, "codigo-de-conduta")
    message = f"{role.mention} - https://python.org.br/cdc"
    await ctx.channel.send(messages.CDC.format(
        cdc_team=role.mention
    ))
