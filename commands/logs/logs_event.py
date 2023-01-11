import discord
from discord.ext import commands

from functions import Utils

class LogsEvent(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    # === Event ===
    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event: discord.ScheduledEvent):
        # Vérifications         
        if not self.utils.get_server_config(event.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(event.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un événement à été créé", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("add"))

        embed.add_field(name="Nom de l'événement", value=event.name, inline=True)
        embed.add_field(name="Url", value=event.url, inline=True)

        if event.description is not None:
            embed.add_field(name="Description de l'événement", value=event.description, inline=True)

        if event.creator is not None:
            embed.add_field(name="Créateur", value=event.creator.mention, inline=True)

        timezone_start_date = self.utils.apply_timezone(event.start_time)
        embed.add_field(name="Date de début", value=f"`{timezone_start_date.strftime('%d/%m/%Y %H:%M:%S')}` soit <t:{int(timezone_start_date.timestamp())}:R>", inline=False)

        if event.end_time is not None:
            timezone_expiration_date = self.utils.apply_timezone(event.end_time)
            embed.add_field(name="Date de fin", value=f"`{timezone_expiration_date.strftime('%d/%m/%Y %H:%M:%S')}` soit <t:{int(timezone_expiration_date.timestamp())}:R>", inline=False)

        if event.cover_image is not None:
            embed.set_thumbnail(url=event.cover_image.url)

        if event.location is not None:
            embed.add_field(name="Localisation", value=event.location, inline=True)

        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_scheduled_event_delete(self, event: discord.ScheduledEvent):
        # Vérifications         
        if not self.utils.get_server_config(event.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(event.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un événement à été supprimé", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("remove"))

        embed.add_field(name="Nom de l'événement", value=event.name, inline=True)
        embed.add_field(name="Url", value=event.url, inline=True)

        if event.description is not None:
            embed.add_field(name="Description de l'événement", value=event.description, inline=True)

        if event.creator is not None:
            embed.add_field(name="Créateur", value=event.creator.mention, inline=True)

        timezone_start_date = self.utils.apply_timezone(event.start_time)
        embed.add_field(name="Date de début", value=f"`{timezone_start_date.strftime('%d/%m/%Y %H:%M:%S')}` soit <t:{int(timezone_start_date.timestamp())}:R>", inline=False)

        if event.end_time is not None:
            timezone_expiration_date = self.utils.apply_timezone(event.end_time)
            embed.add_field(name="Date de fin", value=f"`{timezone_expiration_date.strftime('%d/%m/%Y %H:%M:%S')}` soit <t:{int(timezone_expiration_date.timestamp())}:R>", inline=False)

        if event.cover_image is not None:
            embed.set_thumbnail(url=event.cover_image.url)

        if event.location is not None:
            embed.add_field(name="Localisation", value=event.location, inline=True)

        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before: discord.ScheduledEvent, after: discord.ScheduledEvent):
        # Vérifications         
        if not self.utils.get_server_config(after.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(after.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un événement à été modifié", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("edit"))

        if before.description != after.description:
            embed.add_field(name="Description de l'événement", value=f"Avant : {before.description}\nAprès : {after.description}", inline=True)
        
        if before.channel != after.channel:
            embed.add_field(name="Salon", value=f"Avant : {before.channel.mention if before.channel else 'Aucun'}\nAprès : {after.channel.mention if after.channel else 'Aucun'}", inline=True)
        
        if before.cover_image != after.cover_image:
            embed.add_field(name="Image de couverture", value=f"Avant : {before.cover_image.url if before.cover_image else 'Aucune'}\nAprès : {after.cover_image.url if after.cover_image else 'Aucune'}", inline=True)
        
        if before.end_time != after.end_time:
            embed.add_field(name="Date de fin", value=f"Avant : {before.end_time}\nAprès : {after.end_time}", inline=True)
        
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsEvent(bot))
