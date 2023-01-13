from typing import Literal

import discord
from discord.ext import commands

from functions import Utils

class LogsThread(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    def checks(self, thread: discord.Thread) -> discord.TextChannel:
            if not self.utils.get_server_config(thread.guild.id, "logs", "active"):
                return None

            logs_channel = self.utils.get_server_config(thread.guild.id, "logs", "channel_id")
            logs_channel = self.client.get_channel(int(logs_channel))
            return logs_channel


    def create_embed(self, thread: discord.Thread, type: Literal["create", "delete", "update"]) -> discord.Embed:
        """Créer un embed en fonction du type d'action

        Args:
            channel (discord.abc.GuildChannel): Le salon qui créé/modifié/supprimé
            type (Literal["create", "delete", "update"]): le type d'action 

        Returns:
            discord.Embed: L'embed entier
        """
        title = "Un Thread a été "
        if type == "create":
            title += "créé"
            image = "add"
        elif type == "delete":
            title += "supprimé"
            image = "trash"
        elif type == "update":
            title += "modifié"
            image = "edit"

        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=title, icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img(image))

        embed.add_field(name="Nom", value=thread.name, inline=True)

        if thread.owner is not None:
            embed.add_field(name="Créateur", value=thread.owner.mention, inline=True)

        # ajout du salon et de la date
        if type != "delete":
            embed.add_field(name="Salon", value=thread.mention, inline=False)

        return embed


    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        logs_channel = self.checks(thread)
        if logs_channel is None:
            return

        embed = self.create_embed(thread, "create")
        embed.add_field(name=self.utils.invisible_string(), value=thread.mention + " - " + self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_thread_delete(self, thread: discord.Thread):
        logs_channel = self.checks(thread)
        if logs_channel is None:
            return

        embed = self.create_embed(thread, "delete")
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
        logs_channel = self.checks(before)
        if logs_channel is None:
            return

        # création de la base de l'embed
        embed = self.create_embed(before, "update")

        # ajout des informations
        if before.name != after.name:
            embed.add_field(name="Nom", value=f"Avant: {before.name}\nAprès: {after.name}", inline=False)
        
        if before.slowmode_delay != after.slowmode_delay:
            embed.add_field(name="Slowmode", value=f"Avant: {before.slowmode_delay}\nAprès: {after.slowmode_delay}", inline=False)

        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsThread(bot))
