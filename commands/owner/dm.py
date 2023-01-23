from discord.ext import commands

from functions import Utils
from functions import is_me

class Dm(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    async def command(self, ctx: commands.Context, mention, msg: str):
        member = ctx.guild.get_member(int(self.utils.replaces(mention, "<@", "", ">", "", "!", "")))

        if member is None:
            await ctx.send("Vous n'avez pas mentionné un joueur !")

        await member.send(msg)
        await ctx.message.add_reaction("✅")


    @commands.command()
    @commands.check(is_me)
    async def dm(self, ctx, mention, *, msg):
        await self.command(ctx, mention, msg)


async def setup(bot):
    await bot.add_cog(Dm(bot))
