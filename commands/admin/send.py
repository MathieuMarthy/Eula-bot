import discord
from discord import app_commands
from discord.ext import commands


class Send(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    async def command(self, ctx: commands.Context, channel: discord.TextChannel, message: str):
        try:
            await channel.send(message)
        except discord.errors.HTTPException as e:
            await ctx.send(f"Une erreur est survenue avec le message:\n`{e}`")
            return


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def send(self, ctx, channel, *, json: str):
        channel = channel.replace("<", "").replace("#", "").replace(">", "")
        channel = await self.client.fetch_channel(channel)

        if channel is None:
            await ctx.send("Le salon est invalide")
            return

        await self.command(ctx, channel, json)


    @app_commands.command(name="send", description="Envoie un message dans un salon")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="le salon dans lequel envoyer le message")
    @app_commands.describe(message="le message à envoyer")
    async def sendSlash(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, channel, message)


async def setup(bot):
    await bot.add_cog(Send(bot))
