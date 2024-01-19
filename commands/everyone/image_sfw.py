import enum

import discord
from discord import app_commands
from discord.ext import commands
from Services.imageNeko.imageNekos import ImageNekos

from data import config


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


    async def command(self, ctx: commands.Context, tag: str, nb: str = "1"):
         for _ in range(nb):
            text = self.get_image(tag, False)
            if "\n" in text:
                break

            await ctx.send(text)


    @commands.command()
    async def image_sfw(self, ctx: commands.Context, tag: str, nb: str = "1"):
        if not nb.isdigit():
            await ctx.send("Nb doit être un nombre !")
            return

        nb = int(nb)
        if nb > 20 and ctx.author.id != config.owner_id:
            nb = 20
            await ctx.send("Le maximum est de 20")
        await self.command(ctx, tag)


    @app_commands.command(name="image_sfw", description="envoie une image d'animé aléatoire")
    @app_commands.describe(tag="La catégorie de l'image")
    @app_commands.describe(nombre_images="le nombre d'images à envoyer")
    async def image_sfwSlash(self, interaction: discord.Interaction, tag: Tags, nombre_images: app_commands.Range[int, 1, 20] = 1):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, tag.value, nombre_images)


async def setup(bot):
    await bot.add_cog(ImageSfw(bot))
