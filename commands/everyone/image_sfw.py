import enum

import discord
from discord import app_commands
from discord.ext import commands

from parentsClasses.imageNekos import ImageNekos


class Tags(enum.Enum):
    kiss = "kiss"
    lick = "lick"
    hug = "hug"
    baka = "baka"
    cry = "cry"
    poke = "poke"
    smug = "smug"
    slap = "slap"
    tickle = "tickle"
    pat = "pat"
    laugh = "laugh"
    feed = "feed"
    cuddle = "cuddle"


class ImageSfw(ImageNekos):
    def __init__(self, bot):
        super().__init__(bot)

        self.error_msg = "\n".join(self.sfw_tags)


    async def command(self, ctx: commands.Context, tag: str):
        text = self.get_image(tag, False)
        await ctx.send(text)


    @commands.command()
    async def image_sfw(self, ctx: commands.Context, tag: str):
        await self.command(ctx, tag)


    @app_commands.command(name="image_sfw", description="envoie une image d'animé aléatoire")
    @app_commands.describe(tag="La catégorie de l'image")
    async def image_sfwSlash(self, interaction: discord.Interaction, tag: Tags):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, tag.value)


async def setup(bot):
    await bot.add_cog(ImageSfw(bot))
