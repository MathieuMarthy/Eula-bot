import enum

import discord
from discord import app_commands
from discord.ext import commands

from parentsClasses.imageNekos import ImageNekos
from data import config

class Tags(enum.Enum):
    irl = "4K"
    ass = "ass"
    blowjob = "blowjob"
    boobs = "boobs"
    cum = "cum"
    feet = "feet"
    hentai = "hentai"
    wallpapers = "wallpapers"
    spank = "spank"
    gasm = "gasm"
    lesbian = "lesbian"
    lewd = "lewd"
    pussy = "pussy"


class ImageNsfw(ImageNekos):
    def __init__(self, bot):
        super().__init__(bot)

        self.error_msg = "\n".join(self.nsfw_tags)


    async def command(self, ctx: commands.Context, tag: str, nb: int):
        if not ctx.channel.is_nsfw() and ctx.author.id != config.owner_id:
            await ctx.send("Le salon doit être nsfw !")
            return

        for _ in range(nb):
            text = self.get_image(tag, True)
            if "\n" in text:
                break

            await ctx.send(text)


    @commands.command()
    async def image_nsfw(self, ctx: commands.Context, tag: str, nb: str="1"):
        if not nb.isdigit():
            await ctx.send("Nb doit être un nombre !")
            return

        nb = int(nb)
        if nb > 20 or ctx.author.id != config.owner_id:
            nb = 20
            await ctx.send("Le maximum est de 20")

        await self.command(ctx, tag, nb)


    @app_commands.command(name="image_nsfw", description="envoie une d'animé image nsfw aléatoire")
    @app_commands.describe(tag="La catégorie de l'image")
    @app_commands.describe(nombre_images="le nombre d'images à envoyer")
    async def image_nsfwSlash(self, interaction: discord.Interaction, tag: Tags, nombre_images: app_commands.Range[int, 1, 20] = 1):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, tag.value, nombre_images)


async def setup(bot):
    await bot.add_cog(ImageNsfw(bot))
