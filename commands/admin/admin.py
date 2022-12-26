import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Admin(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client 

    @commands.command()
    async def sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"{len(fmt)} commandes synchronisées")

    # @app_commands.command(name="ping", description="ping le bot")
    # async def ping(self, interaction=discord.Interaction):
    #     if arg.isdigit():
    #         await ctx.channel.purge(limit=int(arg) + 1)
    #     else:
    #         tmp = 0
    #         async for message in ctx.history(limit=500):
    #             tmp += 1
    #             if message.jump_url == arg:
    #                 await ctx.send(
    #                     f"{tmp - 2} messages sélectionnés jusqu'au message demandé. voulez-vous les supprimer ? (oui/non)")
    #                 msg = await client.wait_for("message", check=lambda message: message.author == ctx.author)
    #                 if msg.content.lower() in ["oui", "o", "y", "yes"]:
    #                     await ctx.channel.purge(limit=tmp + 1)
    #                 else:
    #                     await msg.add_reaction("✅")
    #                 return

async def setup(bot):
    await bot.add_cog(Admin(bot))
