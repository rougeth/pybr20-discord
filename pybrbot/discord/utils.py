import asyncio
import functools
import logging

from . import config
from loguru import logger

import discord

SPEAKER_ROLE = 768425216124649472


def generate_role_index(roles):
    index = {}
    for role, invite_codes in roles:
        index.update({code: role for code in invite_codes})

    return index


class InviteTracker:
    def __init__(self, client):
        self.client = client
        self.old_invites = {}
        self.invites = {}
        self.invite_codes = {}

    async def fetch_roles(self):
        # Available roles
        guild = await self.client.fetch_guild(config.GUILD)
        roles = {role.name: role.id for role in guild.roles}

        # Fetch role ID from role name
        invite_codes = generate_role_index(
            [
                config.ROLE_ORG,
                config.ROLE_CDC,
                config.ROLE_SPEAKER,
                config.ROLE_TUTORIAL,
            ]
        )
        code_role_ids = {}

        for code, role_name in invite_codes.items():
            code_role_ids[code] = roles[role_name]

        return code_role_ids

    async def get_invites(self):
        guild = await self.client.fetch_guild(config.GUILD)
        invites = await guild.invites()
        return {invite.code: invite.uses for invite in invites}

    async def sync(self):
        logger.info("Syncing invite codes usage")

        invites = await self.get_invites()
        self.old_invites = self.invites
        self.invites = invites

    def diff(self):
        diff = {}
        for code, uses in self.invites.items():
            old_uses = self.old_invites.get(code, 0)
            if uses > old_uses:
                diff[code] = uses - old_uses
                logger.info(f"Invite code used. code={code}, uses={uses}")

        return diff

    async def check_member_role(self, member):
        logger.info(f"Checking member role. member={member.display_name}")

        if not self.invite_codes:
            logger.info("Fetching roles")
            self.invite_codes = await self.fetch_roles()

        await self.sync()
        invite_diff = self.diff()

        for code, uses in invite_diff.items():
            logger.info(f"Invite code used. code={code}")
            try:
                new_role = discord.Object(self.invite_codes.get(code))
            except TypeError:
                logger.error(
                    f"code not in invite_codes, ignoring. code={code!r}, invite_codes={self.invite_codes!r}"
                )
                return None

            if new_role and uses == 1:
                logger.info(
                    f"Updating member role. member={member.display_name}, role={new_role}"
                )
                await member.add_roles(new_role)
                return new_role
            elif uses > 1:
                logger.warning(
                    "Two or more users joined server between invite tracker updates."
                )

        return None


def get_role(guild, role_name):
    roles = {role.name: role for role in guild.roles}
    return roles.get(role_name)


def cmdlog(f):
    @functools.wraps(f)
    async def wrapper(ctx, *args, **kwargs):
        logger.info(f"/{f.__name__} command trigger by user. user={ctx.message.author!r}")
        await f(ctx, *args, **kwargs)

    return wrapper
