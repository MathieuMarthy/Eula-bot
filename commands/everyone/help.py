import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils
from view.helpSelect import HelpView

class Help(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    async def command(self, ctx):
        view = HelpView(self.client)
        embed = await view.default_embed()
        await ctx.send(embed=embed, view=view)


    @commands.command()
    async def help(self, ctx):
        await self.command(ctx)


    @app_commands.command(name="help", description="menu interactif d'aide")
    async def helpSlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx)


async def setup(bot):
    await bot.add_cog(Help(bot))
