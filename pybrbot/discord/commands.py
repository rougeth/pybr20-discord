import discord
from discord.ext.commands import Cog, command
from loguru import logger

CDC_ROLE = "codigo-de-conduta"
CDC_CHANNEL = "cdc"


class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def cdc(self, ctx, *args):
        role = discord.utils.get(ctx.guild.roles, name=CDC_ROLE)
        message = await ctx.channel.send(role.mention)

        channel = discord.utils.get(ctx.guild.channels, name=CDC_CHANNEL)
        await channel.send(
            f"🚨 **Atenção!**\nAlerta enviado pela pessoa: {ctx.message.author.mention}\nLink para mensagem: {message.jump_url}"
        )
        logger.info(
            f"CDC Warning send. message={message.jump_url!r}, author={ctx.message.author.mention!r}"
        )
        await ctx.message.delete()
