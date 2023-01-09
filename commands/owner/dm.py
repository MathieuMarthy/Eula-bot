import os

import discord
from discord.ext import commands

from functions import Utils
from functions import is_me

class Dm(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    async def command(self, ctx: commands.Context, msg: str):
        member = await self.client.fetch_user(ctx.message.mentions[0].id)

        if member is None:
            await ctx.send("Vous n'avez pas mentionné un joueur !")

        await member.send(msg)
        await ctx.message.add_reaction("✅")


    @commands.command()
    @commands.check(is_me)
    async def dm(self, ctx, msg):
        await self.command(ctx, msg)


    @dm.error
    async def set_pp_error(self, ctx, error):
        pass


async def setup(bot):
    await bot.add_cog(Dm(bot))
