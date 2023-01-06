import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Ping(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    async def command(self, ctx):
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name="ping", icon_url=self.client.user.avatar.url)
        embed.set_thumbnail(url=Utils.get_img("power"))
        embed.add_field(name="󠀮 ", value="**Je suis connecté !**", inline=True)
        await ctx.reply(embed=embed, mention_author=False)


    @commands.command()
    async def ping(self, ctx):
        await self.command(ctx)


    @app_commands.command(name="ping", description="ping le bot")
    async def pingSlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx)


async def setup(bot):
    await bot.add_cog(Ping(bot))
