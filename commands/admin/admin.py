import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Admin(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client 

async def setup(bot):
    await bot.add_cog(Admin(bot))
