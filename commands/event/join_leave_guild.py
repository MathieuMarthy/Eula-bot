import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class JoinLeaveGuild(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        print("guild join")
        if self.utils.server_exists_in_config(guild.id):
            return
        
        self.utils.add_new_server(guild.id)


    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        print("guild remove")
        if not self.utils.server_exists_in_config(guild.id):
            return

        for config in self.utils.get_server_config(guild.id):
            self.utils.set_server_config(guild.id, config, "active", False)


async def setup(bot):
    await bot.add_cog(JoinLeaveGuild(bot))
