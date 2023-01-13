from random import choice

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class PileOuFace(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    async def command(self, ctx):
        embed = discord.Embed(color=self.utils.embed_color())

        if choice([True, False]):
            embed.add_field(name=f"󠀮Pile", value=" ", inline=True)
            embed.set_image(url=self.utils.get_img("pile"))
        else:
            embed.add_field(name=f"󠀮Face", value=" ", inline=True)
            embed.set_image(url=self.utils.get_img("face"))

        await ctx.reply(embed=embed, mention_author=False)


    @commands.command()
    async def pile_ou_face(self, ctx):
        await self.command(ctx)


    @app_commands.command(name="pile_ou_face", description="pile_ou_face")
    async def pile_ou_faceSlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx)


async def setup(bot):
    await bot.add_cog(PileOuFace(bot))
