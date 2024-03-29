import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Rolevocal(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if not self.utils.get_server_config(member.guild.id, "rolevocal", "active"):
            return

        role = member.guild.get_role(self.utils.get_server_config(member.guild.id, "rolevocal", "role_id"))
        if role is None:
            return
        

        # si l'utilisateur rejoint un salon
        if before.channel is None:
            await member.add_roles(role, reason="rolevocal")

        # si l'utilisateur quitte un salon
        elif after.channel is None:
            await member.remove_roles(role, reason="rolevocal")


async def setup(bot):
    await bot.add_cog(Rolevocal(bot))
