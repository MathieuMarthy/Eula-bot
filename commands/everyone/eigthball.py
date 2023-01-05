from random import choice

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Eightball(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    async def command(self, ctx):
        phrases = [
            "Une chance sur deux", "D'après moi oui", "C'est certain", "Oui absolument", "Sans aucun doute",
            "Très probable", "Oui", "C'est bien parti", "C'est non", "Peu probable", "Faut pas rêver", "N'y compte pas",
            "Impossible"
        ]

        await ctx.reply(choice(phrases), mention_author=False)


    @commands.command(aliases=["8ball", "8b"])
    async def eightball(self, ctx):
        await self.command(ctx)


    @app_commands.command(name="8ball", description="la boule magique répond à vos questions")
    async def eightballSlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx)


async def setup(bot):
    await bot.add_cog(Eightball(bot))
