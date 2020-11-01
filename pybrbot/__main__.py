from pybrbot import discord
from loguru import logger


if __name__ == "__main__":
    if discord.config.SENTRY_URL:
        logger.info("Enabling Sentry integration")
        import sentry_sdk
        sentry_sdk.init(discord.config.SENTRY_URL)

    discord.close_empty_tables.start()
    discord.bot.run(discord.config.TOKEN)
