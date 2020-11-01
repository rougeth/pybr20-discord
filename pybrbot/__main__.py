from pybrbot import discord


if __name__ == "__main__":
    discord.close_empty_tables.start()
    discord.bot.run(discord.config.TOKEN)
