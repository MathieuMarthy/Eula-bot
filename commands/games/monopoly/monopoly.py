import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Monopoly(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    async def command(self, ctx):
       pass


    @commands.command()
    async def monopoly(self, ctx):
        await self.command(ctx)


    @app_commands.command(name="monopoly", description="monopoly jusqu'à 4 joueurs")
    async def monopolySlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx)


async def setup(bot):
    await bot.add_cog(Monopoly(bot))
