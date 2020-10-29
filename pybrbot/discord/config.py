import toml
from decouple import config
from loguru import logger

TOKEN = config('DISCORD_TOKEN')
GUILD = config("DISCORD_GUILD_ID")
CONFIG_FILE = config("CONFIG_FILE", "config/dev.toml")

local_config = toml.load(CONFIG_FILE)
locals().update(local_config)
logger.info(f"Config file loaded. CONFIG_FILE={CONFIG_FILE!r}")
