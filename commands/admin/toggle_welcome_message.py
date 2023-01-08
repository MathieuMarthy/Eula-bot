import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class ToggleWelcomeMessage(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    async def command(self, ctx):
        welcome_message_is_active = self.utils.get_server_config(ctx.guild.id, "welcome_message_state", "active")

        # si le message de bienvenue est activé, on le désactive
        if welcome_message_is_active:
            self.utils.set_server_config(ctx.guild.id, "welcome_message_state", "active", value=False)
            await ctx.send("Le message de bienvenue est maintenant désactivé")
        else:
            msg_content = self.utils.get_server_config(ctx.guild.id, "welcome_message_state", "message")

            # si le message de bienvenue est déjà configuré, on demande si on veut le changer
            if msg_content is not None:
                await ctx.send(f"Le message de bienvenue est déjà configuré, message:\n\n{msg_content}\n\voulez-vous le changer ? (oui/non)")

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
                
                # si on change pas le message, on sauvegarde et on quitte
                if msg.content in ["n", "no", "non"]:
                    await ctx.send("Le message de bienvenue est maintenant activé")
                    self.utils.set_server_config(ctx.guild.id, "welcome_message_state", "active", value=True)
                    return
        
            # on demande le message de bienvenue
            await ctx.send("Entrez le message de bienvenue, vous pouvez utilisez la variable {user} (a mettre avec les accolades) pour écrire le nom de l'utilisateur")
            try:
                msg = await self.client.wait_for(
                    "message",
                    check=lambda msg: msg.author == ctx.author and msg.channel == ctx.channel,
                    timeout=300)
                
            except asyncio.TimeoutError:
                await ctx.send("Vous avez mis trop de temps à répondre")
                return
            
            # on sauvegarde le message
            self.utils.set_server_config(ctx.guild.id, "welcome_message_state", "message", value=msg.content)
            self.utils.set_server_config(ctx.guild.id, "welcome_message_state", "active", value=True)
            await ctx.send("Le message de bienvenue est maintenant activé")



    @commands.command()
    @commands.has_permissions(administrator=True)
    async def toggle_welcome_message(self, ctx):
        await self.command(ctx)


    @app_commands.command(name="toggle_welcome_message", description="active ou désactive le message de bienvenue")
    @app_commands.checks.has_permissions(administrator=True)
    async def toggle_welcome_messageSlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx)


    @toggle_welcome_message.error
    async def help_send_embedError(self, ctx, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await ctx.send(error_string)
        else:
            raise error


    @toggle_welcome_messageSlash.error
    async def help_send_embedSlashError(self, interaction, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await interaction.response.send_message(error_string, ephemeral=True)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(ToggleWelcomeMessage(bot))
