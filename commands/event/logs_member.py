import os
from PIL import Image

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class LogsMember(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    # === Member ===
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Vérifications         
        if not self.utils.get_server_config(member.guild.id, "logs", "active"):
            return

        logs_channel = self.utils.get_server_config(member.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Un membre a rejoint le serveur", icon_url=member.avatar.url)
        embed.set_thumbnail(url=self.utils.get_img("notif"))

        embed.add_field(name="Membre", value=member.mention, inline=True)
        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsMember(bot))
