import discord
from discord.ext import commands

from functions import Utils

class Autorole(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return

        autorole_is_active = self.utils.get_server_config(member.guild.id, "autorole", "active")

        if autorole_is_active:
            role_id = self.utils.get_server_config(member.guild.id, "autorole", "role_id")
            role = member.guild.get_role(role_id)

            if role is not None:
                await member.add_roles(role)


async def setup(bot):
    await bot.add_cog(Autorole(bot))
