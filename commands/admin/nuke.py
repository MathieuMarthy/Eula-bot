import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Nuke(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils.get_instance(client)
    
    async def command(self, ctx: commands.Context, channel: discord.TextChannel):
        await ctx.send(f"Voulez-vous vraiment supprimer le salon {channel.mention}? (oui/non)")

        try:
            msg = await self.client.wait_for(
                "message",
                check=lambda msg: msg.author == ctx.author and
                                    msg.channel == ctx.channel and
                                    msg.content.lower() in ["y", "o", "n", "yes", "oui", "no", "non"],
                timeout=300)

        except asyncio.TimeoutError:
            await ctx.send("Vous avez mis trop de temps à répondre")
            return

        # si on change pas le rôle, on sauvegarde et on quitte
        if msg.content in ["n", "no", "non"]:
            await msg.add_reaction("✅")
            return

        await channel.delete()

        await ctx.guild.create_text_channel(
            channel.name,
            overwrites=channel.overwrites,
            category=channel.category,
            topic=channel.topic,
            slowmode_delay=channel.slowmode_delay,
            nsfw=channel.is_nsfw(),
            reason="Nuke command",
        )

        await msg.add_reaction("✅")



    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nuke(self, ctx: commands.Context, channel: str):
        channel = channel.replace("<", "").replace("#", "").replace(">", "")
        channel = ctx.guild.get_channel(int(channel))

        if channel is None:
            await ctx.send("Le salon est invalide")
            return

        await self.command(ctx, channel)


    @app_commands.command(name="nuke", description="ADMIN, supprimer un salon et le recréer avec les mêmes paramètres")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="le salon à supprimer et recréer")
    async def nukeSlash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, channel)
    

    @nuke.error
    async def nukeError(self, ctx, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await ctx.send(error_string)
        else:
            raise error


    @nukeSlash.error
    async def nukeSlashError(self, interaction, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await interaction.response.send_message(error_string, ephemeral=True)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Nuke(bot))
