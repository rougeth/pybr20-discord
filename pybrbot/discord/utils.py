import logging

from . import config
from loguru import logger

import discord


class InviteTracker:
    invite_roles = {
        "wMtqbUC": "768425216124649472",  # @palestrante
    }

    def __init__(self, client):
        self.client = client
        self.old_invites = {}
        self.invites = {}

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
                logger.info("Invite code used. code=%r, uses=%r", code, uses)

        return diff

    async def check_member_role(self, member):
        logger.info("Checking member role. member=%r", member.display_name)
        await invite_tracker.sync()
        invite_diff = invite_tracker.diff()

        for code, uses in invite_diff.items():
            logger.info("Invite code used. code=%r", code)
            new_role = discord.Object(INVITES_ROLES.get(code))
            if new_role and uses == 1:
                logger.info("Updating member role. member=%r, role=%r", member.display_name, new_role)
                await member.add_roles(new_role)
            elif uses > 1:
                logger.warning("Two or more users joined server between invite tracker updates.")



def get_role(guild, role_name):
    roles = {role.name: role for role in guild.roles}
    return roles.get(role_name)
