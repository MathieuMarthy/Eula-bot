import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class ToggleLogs(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    async def command(self, ctx: commands.Context):
        logs_is_active = self.utils.get_server_config(ctx.guild.id, "logs", "active")

        if logs_is_active:
            self.utils.set_server_config(ctx.guild.id, "logs", "active", value=False)
            await ctx.send("Les logs sont maintenant désactivées")
        else:
            channel_id = self.utils.get_server_config(ctx.guild.id, "logs", "channel_id")
            channel = ctx.guild.get_channel(channel_id)

            if channel is not None:
                await ctx.send(f"Le salon de logs est déjà configuré\nChannel: **{channel.mention}**\nVoulez-vous le changer ? (oui/non)")

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
                    await ctx.send(f"Le salon des logs est maintenant **{channel.mention}**")
                    self.utils.set_server_config(ctx.guild.id, "logs", "active", value=True)
                    return

            await ctx.send("Veuillez mentionner le salon")

            try:
                msg = await self.client.wait_for(
                    "message",
                    check=lambda msg: msg.author == ctx.author and
                                      msg.channel == ctx.channel,
                    timeout=300)

            except asyncio.TimeoutError:
                await ctx.send("Vous avez mis trop de temps à répondre")
                return

            channel = self.utils.replaces(msg.content, "<#", "", ">", "")
            channel = ctx.guild.get_channel(int(channel))

            if channel is None:
                await ctx.send("Le salon n'existe pas")
                return


            self.utils.set_server_config(ctx.guild.id, "logs", "channel_id", value=channel.id)
            self.utils.set_server_config(ctx.guild.id, "logs", "active", value=True)
            await ctx.send(f"Le salon des logs est maintenant **{channel.name}**")


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def toggle_logs(self, ctx):
        await self.command(ctx)


    @app_commands.command(name="toggle_logs", description="ADMIN, active ou désactive les logs")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def toggle_logsSlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx)


    @toggle_logs.error
    async def toggle_logsError(self, ctx, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await ctx.send(error_string)
        else:
            raise error


    @toggle_logs.error
    async def toggle_logsSlashError(self, interaction, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await interaction.response.send_message(error_string, ephemeral=True)
        else:
            raise error



async def setup(bot):
    await bot.add_cog(ToggleLogs(bot))
