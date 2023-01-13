import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Send(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    async def command(self, ctx: commands.Context, channel: discord.TextChannel, message: str):
        try:
            await channel.send(message)
        except discord.errors.HTTPException as e:
            await ctx.send(f"Une erreur est survenue avec le message:\n`{e}`")
            return
        
        await ctx.reply("✅ Message envoyé", mention_author=False)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def send(self, ctx: commands.Context, channel, *, json: str):
        channel = channel.replace("<", "").replace("#", "").replace(">", "")
        channel = ctx.guild.get_channel(int(channel))

        if channel is None:
            await ctx.send("Le salon est invalide")
            return

        await self.command(ctx, channel, json)


    @app_commands.command(name="send", description="ADMIN, Envoie un message dans un salon")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="le salon dans lequel envoyer le message")
    @app_commands.describe(message="le message à envoyer")
    async def sendSlash(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, channel, message)


    @send.error
    async def sendError(self, ctx, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await ctx.send(error_string)
        else:
            raise error


    @sendSlash.error
    async def sendSlashError(self, interaction, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await interaction.response.send_message(error_string, ephemeral=True)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Send(bot))
