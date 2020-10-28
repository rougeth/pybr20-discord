import logging

from . import config
from loguru import logger

import discord

SPEAKER_ROLE = 768425216124649472
ORG_ROLE = 767873391650537533
TUTORIAL_ROLE = 771000495409594388

class InviteTracker:
    invite_roles = {
        "wMtqbUC": SPEAKER_ROLE,  # @palestrante
        "x6q9ryY": ORG_ROLE,  # @organização
        's3s9kD7': TUTORIAL_ROLE,
        'YyHK6PX': TUTORIAL_ROLE,
        '48VfBAD': TUTORIAL_ROLE,
        'tztKmzp': TUTORIAL_ROLE,
        'xPWBPzP': TUTORIAL_ROLE,
        'JGjNmgW': TUTORIAL_ROLE,
        'jaJTTVr': TUTORIAL_ROLE,
        '73k35eh': TUTORIAL_ROLE,
        'gybvTj2': TUTORIAL_ROLE,
        '3fjCpNp': TUTORIAL_ROLE,
        'gUpxWGC': TUTORIAL_ROLE,
        'fmvChdY': TUTORIAL_ROLE,
        'TnAKpNN': TUTORIAL_ROLE,
        'WTStKnz': TUTORIAL_ROLE,
        'TCufqKy': TUTORIAL_ROLE,
        'ryN5RDY': TUTORIAL_ROLE,
        'uMk25pQ': TUTORIAL_ROLE,
        'YeJ46VC': TUTORIAL_ROLE,
        'FNk4ybp': TUTORIAL_ROLE,
        'ktpK54x': TUTORIAL_ROLE,
        'dczjb5H': TUTORIAL_ROLE,
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
                logger.info(f"Invite code used. code={code}, uses={uses}")

        return diff

    async def check_member_role(self, member):
        logger.info(f"Checking member role. member={member.display_name}")
        await self.sync()
        invite_diff = self.diff()

        for code, uses in invite_diff.items():
            logger.info(f"Invite code used. code={code}")
            new_role = discord.Object(self.invite_roles.get(code))
            if new_role and uses == 1:
                logger.info(f"Updating member role. member={member.display_name}, role={new_role}")
                await member.add_roles(new_role)
                return new_role
            elif uses > 1:
                logger.warning("Two or more users joined server between invite tracker updates.")

        return None


def get_role(guild, role_name):
    roles = {role.name: role for role in guild.roles}
    return roles.get(role_name)
