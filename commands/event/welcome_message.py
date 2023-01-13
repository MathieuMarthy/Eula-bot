import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class WelcomeMessage(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome_message_is_active = self.utils.get_server_config(member.guild.id, "welcome_message", "active")

        if welcome_message_is_active:
            welcome_message = self.utils.get_server_config(member.guild.id, "welcome_message", "message")
            welcome_message = welcome_message.replace("{user}", member.name)

            await member.send(welcome_message)


async def setup(bot):
    await bot.add_cog(WelcomeMessage(bot))
