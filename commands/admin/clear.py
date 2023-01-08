import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Clear(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils(client)
    
    async def command(self, ctx: commands.Context, arg):
        if arg.isdigit():
            await ctx.channel.purge(limit=int(arg) + 1)
        else:
            if ctx.interaction is not None:
                await ctx.interaction.response.defer()

            index = 0
            async for message in ctx.history(limit=500):
                index += 1
                if message.jump_url == arg:
                    await ctx.send(
                        f"{index - 2} messages sélectionnés jusqu'au message demandé. voulez-vous les supprimer ? (oui/non)")
                    msg = await self.client.wait_for("message", check=lambda message: message.author == ctx.author)
                    if msg.content.lower() in ["oui", "o", "y", "yes"]:
                        await ctx.channel.purge(limit=index)
                        return
                    else:
                        await msg.add_reaction("✅")
                    return
            await ctx.send("Message non trouvé")


    @commands.command(aliases=["c"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, arg="1"):
        await self.command(ctx, arg)


    @app_commands.command(name="clear", description="Supprime un nombre de messages, ou jusqu'à un message donné")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(nombre_ou_url_message="nombre de messages à supprimer ou url du message jusqu'auquel supprimer. Par défaut, 1 message")
    async def clearSlash(self, interaction: discord.Interaction, nombre_ou_url_message: str = "1"):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, nombre_ou_url_message)
    

    @clear.error
    async def clearError(self, ctx, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await ctx.send(error_string)
        else:
            raise error


    @clearSlash.error
    async def clearSlashError(self, interaction, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await interaction.response.send_message(error_string, ephemeral=True)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Clear(bot))
