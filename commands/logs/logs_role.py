import discord
from discord.ext import commands

from functions import Utils

class LogsRole(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    # === Role ===
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        # Vérifications         
        if not self.utils.get_server_config(role.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(role.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un rôle à été créé", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("add"))

        embed.add_field(name="Role", value=role.name, inline=True)
        embed.add_field(name=self.utils.invisible_string(), value=role.mention + " - " + self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        # Vérifications         
        if not self.utils.get_server_config(role.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(role.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un rôle à été supprimé", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("trash"))

        embed.add_field(name="Role", value=role.name, inline=True)
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        # Vérifications         
        if not self.utils.get_server_config(after.guild.id, "logs", "active"):
            return
        
        if (
            before.name == after.name and 
            before.color == after.color
        ):
            return 


        logs_channel = self.utils.get_server_config(after.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un rôle à été modifié", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("edit"))

        embed.add_field(name="Role", value=after.name, inline=True)

        # vérification des changements
        if before.name != after.name:
            embed.add_field(name="Ancien nom", value=before.name, inline=True)
            embed.add_field(name="Nouveau nom", value=after.name, inline=True)
        
        if before.color != after.color:
            embed.add_field(name="Ancienne couleur", value=before.color, inline=True)
            embed.add_field(name="Nouvelle couleur", value=after.color, inline=True)

        embed.add_field(name=self.utils.invisible_string(), value=after.mention + " - " + self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsRole(bot))
