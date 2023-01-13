from typing import Literal

import discord
from discord.ext import commands

from functions import Utils

class LogsChannel(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    def checks(self, channel) -> discord.abc.GuildChannel:
            if channel.guild is None:
                return None

            if not self.utils.get_server_config(channel.guild.id, "logs", "active"):
                return None

            logs_channel = self.utils.get_server_config(channel.guild.id, "logs", "channel_id")
            logs_channel = self.client.get_channel(int(logs_channel))
            return logs_channel


    def create_embed(self, channel: discord.abc.GuildChannel, type: Literal["create", "delete", "update"]) -> discord.Embed:
        """Créer un embed en fonction du type d'action

        Args:
            channel (discord.abc.GuildChannel): Le salon qui créé/modifié/supprimé
            type (Literal["create", "delete", "update"]): le type d'action 

        Returns:
            discord.Embed: L'embed entier
        """
        if type == "create":
            title = "Salon créé"
            image = "add"
        elif type =="delete":
            title = "Salon supprimé"
            image = "trash"
        elif type =="update":
            title = "Salon modifié"
            image = "edit"

        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=title, icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img(image))

        embed.add_field(name="Nom", value=channel.name, inline=True)
        embed.add_field(name="Type", value=channel.type, inline=True)

        # ajout du salon et de la date
        if type != "delete":
            embed.add_field(name="Salon", value=channel.mention, inline=False)

        return embed


    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        logs_channel = self.checks(channel)
        if logs_channel is None:
            return

        embed = self.create_embed(channel, "create")
        embed.add_field(name=self.utils.invisible_string(), value=channel.mention + " - " + self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        logs_channel = self.checks(channel)
        if logs_channel is None:
            return

        embed = self.create_embed(channel, "delete")
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        logs_channel = self.checks(before)
        if logs_channel is None:
            return

        # création de la base de l'embed
        embed = self.create_embed(before, "update")

        # ajout des informations
        if before.name != after.name:
            embed.add_field(name="Nom", value=f"Avant: {before.name}\nAprès: {after.name}", inline=False)
        if before.type != after.type:
            embed.add_field(name="Type", value=f"Avant: {self.translate_type(before.type)}\nAprès: {self.translate_type(after.type)}", inline=False)
        if before.position != after.position:
            embed.add_field(name="Position", value=f"Avant: {before.position}\nAprès: {after.position}", inline=False)
        if before.category != after.category:
            embed.add_field(name="Catégorie", value=f"Avant: {before.category}\nAprès: {after.category}", inline=False)

        # si le salon est textuel
        if isinstance(before, discord.TextChannel):
            if before.topic != after.topic:
                embed.add_field(name="Description", value=f"Avant: {before.topic}\nAprès: {after.topic}", inline=False)
            if before.slowmode_delay != after.slowmode_delay:
                embed.add_field(name="Slowmode", value=f"Avant: {before.slowmode_delay}\nAprès: {after.slowmode_delay}", inline=False)
        
        # si le salon est vocal
        elif isinstance(before, discord.VoiceChannel):
            if before.user_limit != after.user_limit:
                embed.add_field(name="Limite d'utilisateurs", value=f"Avant: {before.user_limit}\nAprès: {after.user_limit}", inline=False)

        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)

    
    def translate_type(self, type: str) -> str:
        if type == "text":
            return "Textuel"
        elif type == "voice":
            return "Vocal"
        elif type == "category":
            return "Catégorie"
        else:
            return "Inconnu"


async def setup(bot):
    await bot.add_cog(LogsChannel(bot))
