import os
from PIL import Image

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class LogsMessage(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    # === Message ===
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        # Vérifications 
        if message.author.bot or message.guild is None:
            return
        
        if not self.utils.get_server_config(message.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(message.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Message supprimé de {message.author.name}", icon_url=message.author.avatar.url)
        embed.set_thumbnail(url=self.utils.get_img("trash"))


        # si le message est vide, il y a seulement des fichiers
        if message.content != "":
            embed.add_field(name="Contenu", value=message.content, inline=True)
        else:
            embed.add_field(name="Contenu", value=f"<Fichier{'s' if len(message.attachments) > 1 else ''}>", inline=False)

        # ajout du salon et de la date
        embed.add_field(name="Salon", value=message.channel.mention, inline=True)
        embed.add_field(name=self.utils.invisible_string(), value=message.author.mention + " - " + self.utils.get_date_time(), inline=False)
    
        # envoie du message
        msg = await logs_channel.send(embed=embed)

        # si le message supprimé contient des fichiers
        if len(message.attachments) > 0:
            for attachement in message.attachments:
                # si le message ne peut pas être envoyé sur le serveur
                if attachement.size > message.guild.filesize_limit:

                    # on envoie en embed pour décrire le fichier
                    embed = discord.Embed(
                        title="Fichier supprimé",
                        description="Le fichier est trop lourd pour être renvoyé par le bot",
                        color=self.utils.embed_color()
                    )
                    embed.add_field(name=f"Nom du fichier: {attachement.filename}", value=f"type de fichier: {attachement.content_type}")

                    await msg.reply(embed=embed)
                
                # sinon on envoie le fichier
                else:
                    await msg.reply(file=await attachement.to_file())
    

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # Vérifications 
        if before.author.bot or before.guild is None:
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
        embed.set_author(name=f"Message modifié de {before.author.name}", icon_url=before.author.avatar.url)
        embed.set_thumbnail(url=self.utils.get_img("edit"))

        embed.add_field(name="Avant", value=before.content, inline=True)
        embed.add_field(name="Après", value=after.content, inline=True)

        # ajout du salon et de la date
        embed.add_field(name="Salon", value=before.channel.mention, inline=False)
        embed.add_field(name=self.utils.invisible_string(), value=after.author.mention + " - " + self.utils.get_date_time() + " - " + f"[lien vers le message]({after.jump_url})", inline=False)
    
        # envoie du message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsMessage(bot))
