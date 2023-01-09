import os

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Setpp(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    async def command(self, ctx: commands.Context):
        if len(ctx.message.attachments) == 0:
            await ctx.send("Aucune image trouvée")
            return

        image: discord.Attachment = ctx.message.attachments[0]

        file_path = os.path.join(self.utils.bot_path(), "tmp", image.filename)
        await image.save(file_path)
        avatar_bytes = open(file_path, "rb").read()

        try:
            await self.client.user.edit(avatar=avatar_bytes)
        except Exception as e:
            await ctx.send(f"Une erreur est survenue: {e}")
            return

        await ctx.message.add_reaction("✅")


    @commands.command()
    async def set_pp(self, ctx):
        await self.command(ctx)


async def setup(bot):
    await bot.add_cog(Setpp(bot))
