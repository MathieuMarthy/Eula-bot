import random

import discord
from discord import app_commands
from discord.ext import commands


class Choisis(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    async def command(self, ctx: commands.Context, propositions):
        list_propositions = propositions.split(",")
        element = random.choice(list_propositions)

        await ctx.send(f"J'ai choisi: {element}")


    @commands.command()
    async def choisis(self, ctx, propositions: str):
        await self.command(ctx, propositions)

    @choisis.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Il manque un argument\nsyntaxe: `choisis <propositions> `")


    @app_commands.command(name="choisis", description="choisis 1 élément entre plusieurs propositions")
    @app_commands.describe(propositions="les propositions, à séparés par des virgules")
    async def choisisSlash(self, interaction: discord.Interaction, propositions: str):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, propositions)


async def setup(bot):
    await bot.add_cog(Choisis(bot))
