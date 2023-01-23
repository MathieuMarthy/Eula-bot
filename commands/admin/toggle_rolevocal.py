import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class ToggleRolevocal(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    async def command(self, ctx: commands.Context):
        rolevocal_is_active = self.utils.get_server_config(ctx.guild.id, "rolevocal", "active")

        if rolevocal_is_active:
            self.utils.set_server_config(ctx.guild.id, "rolevocal", "active", value=False)
            await ctx.send("Le role vocal est maintenant désactivé")
        else:
            role_id = self.utils.get_server_config(ctx.guild.id, "rolevocal", "role_id")
            role = ctx.guild.get_role(role_id)

            if role is not None:
                await ctx.send(f"Le rôle vocal est déjà configuré\nRole: **{role.name}**\nVoulez-vous le changer ? (oui/non)")

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
                    # vérifie si le bot a les permissions
                    if not ctx.guild.me.guild_permissions.manage_roles or ctx.guild.me.top_role < role:
                        await ctx.send("Le bot n'a pas les permissions nécessaires pour donner ce rôle\nLe rôle de Eula doit être plus haut que le rôle à donner")
                        return

                    await ctx.send(f"Le rôle vocal est maintenant **{role.name}**")
                    self.utils.set_server_config(ctx.guild.id, "rolevocal", "active", value=True)
                    return

            await ctx.send("Veuillez mentionner le rôle à donner")

            try:
                msg = await self.client.wait_for(
                    "message",
                    check=lambda msg: msg.author == ctx.author and
                                      msg.channel == ctx.channel,
                    timeout=300)

            except asyncio.TimeoutError:
                await ctx.send("Vous avez mis trop de temps à répondre")
                return

            role = self.utils.replaces(msg.content, "<@&", "", ">", "")
            role = ctx.guild.get_role(int(role))

            if role is None:
                await ctx.send("Le rôle n'existe pas")
                return

            # vérifie si le bot a les permissions
            if not ctx.guild.me.guild_permissions.manage_roles or ctx.guild.me.top_role < role:
                await ctx.send("Le bot n'a pas les permissions nécessaires pour donner ce rôle\nLe rôle de Eula doit être plus haut que le rôle à donner")
                return


            self.utils.set_server_config(ctx.guild.id, "rolevocal", "role_id", value=role.id)
            self.utils.set_server_config(ctx.guild.id, "rolevocal", "active", value=True)
            await ctx.send(f"Le rôle vocal est maintenant **{role.name}**")


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def toggle_rolevocal(self, ctx):
        await self.command(ctx)


    @app_commands.command(name="toggle_rolevocal", description="ADMIN, active ou désactive l'assignation d'un rôle quand un utilisateur rejoint un salon vocal")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def toggle_rolevocalSlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx)


    @toggle_rolevocal.error
    async def toggle_rolevocalError(self, ctx, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await ctx.send(error_string)
        else:
            raise error


    @toggle_rolevocalSlash.error
    async def toggle_rolevocalSlashError(self, interaction, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await interaction.response.send_message(error_string, ephemeral=True)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(ToggleRolevocal(bot))
