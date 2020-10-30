import toml
from decouple import config
from loguru import logger

TOKEN = config("DISCORD_TOKEN")
GUILD = config("DISCORD_GUILD_ID")


# Expected value: "<role name>:<invite_code>,<invite_code>,..."
def role_config_cast(value):
    role_name, invite_codes = value.split(":")
    invite_codes = invite_codes.split(",")
    return role_name, invite_codes


ROLE_SPEAKER = config("ROLE_SPEAKER", cast=role_config_cast, default="palestrante:xyz")
ROLE_ORG = config("ROLE_ORG", cast=role_config_cast, default="organizacao:xyz")
ROLE_CDC = config("ROLE_CDC", cast=role_config_cast, default="codigo-de-conduta:xyz")
ROLE_EVERYONE = config("ROLE_EVERYONE", cast=role_config_cast, default="@everyone:xyz")
ROLE_TUTORIAL = config("ROLE_TUTORIAL", cast=role_config_cast, default="tutoriais:xyz")
