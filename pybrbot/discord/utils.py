from . import config

import discord


class InviteTracker:
    invite_roles = {
        "5JcxDB": "769727469179109406",  # @palestrante
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
        invites = await self.get_invites()
        self.old_invites = self.invites
        self.invites = invites

    def diff(self):
        diff = {}
        for code, uses in self.invites.items():
            old_uses = self.old_invites.get(code, 0)
            if uses > old_uses:
                diff[code] = uses - old_uses

        return diff

    async def check_member_role(self, member):
        await invite_tracker.sync()
        invite_diff = invite_tracker.diff()

        for code, uses in invite_diff.items():
            new_role = discord.Object(INVITES_ROLES.get(code))
            if new_role and uses == 1:
                await member.add_roles(new_role)
            elif uses > 1:
                print("Two or more users joined server between invite tracker updates.")


def get_role(guild, role_name):
    roles = {role.name: role for role in guild.roles}
    return roles.get(role_name)
