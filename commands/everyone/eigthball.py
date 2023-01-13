from random import choice

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Eightball(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    async def command(self, ctx, message: str):
        phrases = [
            "Une chance sur deux", "D'après moi oui", "C'est certain", "Oui absolument", "Sans aucun doute",
            "Très probable", "Oui", "C'est bien parti", "C'est non", "Peu probable", "Faut pas rêver", "N'y compte pas",
            "Impossible"
        ]
        string = f"Q: {message}\nR: {choice(phrases)}"
        await ctx.reply(string, mention_author=False)


    @commands.command(aliases=["8ball", "8b"])
    async def eightball(self, ctx, *, message: str):
        await self.command(ctx, message)


    @app_commands.command(name="8ball", description="la boule magique répond à vos questions")
    @app_commands.describe(message="la question à poser à la boule magique")
    async def eightballSlash(self, interaction: discord.Interaction, message: str):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, message)


async def setup(bot):
    await bot.add_cog(Eightball(bot))
