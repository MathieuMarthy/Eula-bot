import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Autorole(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if not self.utils.get_server_config(member.guild.id, "rolevocal", "active"):
            return

        role = member.guild.get_role(self.utils.get_server_config(member.guild.id, "rolevocal", "role_id"))
        if role is not None:
            return

        # si l'utilisateur rejoint un salon
        if before.channel is None and after.channel is not None:
            member.add_roles(role, reason="rolevocal")
        
        # si l'utilisateur quitte un salon
        elif before.channel is not None and after.channel is None:
            member.remove_roles(role, reason="rolevocal")


async def setup(bot):
    await bot.add_cog(Autorole(bot))
