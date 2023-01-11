import os
from PIL import Image

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class LogsChannel(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)
    
    def translate_type(self, type: str) -> str:
        match type:
            case "text":
                return "Textuel"
            case "voice":
                return "Vocal"
            case "category":
                return "Catégorie"
            case _:
                return "Inconnu"


    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        # Vérifications 
        if channel.guild is None:
            return
        
        if not self.utils.get_server_config(channel.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(channel.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Salon créé", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("add"))

        embed.add_field(name="Nom", value=channel.name, inline=True)
        embed.add_field(name="Type", value=channel.type, inline=True)

        # ajout du salon et de la date
        embed.add_field(name="Salon", value=channel.mention, inline=False)
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        # Vérifications 
        if channel.guild is None:
            return
        
        if not self.utils.get_server_config(channel.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(channel.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Salon supprimé", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("trash"))

        embed.add_field(name="Nom", value=channel.name, inline=True)
        embed.add_field(name="Type", value=channel.type, inline=True)

        # ajout de la date
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)
    
        # envoie du message
        await logs_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        # Vérifications 
        if before.guild is None:
            return
        
        if not self.utils.get_server_config(before.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(before.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return

        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Salon modifié", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("edit"))

        # ajout du salon et de la date
        embed.add_field(name="Salon", value=before.mention, inline=False)
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # ajout des informations
        if before.name != after.name:
            embed.add_field(name="Nom", value=f"Avant: {before.name}\nAprès: {after.name}", inline=False)
        if before.type != after.type:
            embed.add_field(name="Type", value=f"Avant: {self.translate_type(before.type)}\nAprès: {self.translate_type(after.type)}", inline=False)
        if before.topic != after.topic:
            embed.add_field(name="Description", value=f"Avant: {before.topic}\nAprès: {after.topic}", inline=False)
        if before.position != after.position:
            embed.add_field(name="Position", value=f"Avant: {before.position}\nAprès: {after.position}", inline=False)
        if before.category != after.category:
            embed.add_field(name="Catégorie", value=f"Avant: {before.category}\nAprès: {after.category}", inline=False)
        if before.slowmode_delay != after.slowmode_delay:
            embed.add_field(name="Slowmode", value=f"Avant: {before.slowmode_delay}\nAprès: {after.slowmode_delay}", inline=False)
        if before.user_limit != after.user_limit:
            embed.add_field(name="Limite d'utilisateurs", value=f"Avant: {before.user_limit}\nAprès: {after.user_limit}", inline=False)
        
        # envoie du message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsChannel(bot))
