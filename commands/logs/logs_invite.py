import os
from PIL import Image

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class LogsInvite(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    # === Invite ===
    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        # Vérifications         
        if not self.utils.get_server_config(invite.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(invite.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return


        # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Une invitation à été créée", icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img("add"))

        embed.add_field(name="Invitation", value=invite.url, inline=True)
        embed.add_field(name="Créateur", value=invite.inviter.mention, inline=True)

        if invite.expires_at is not None:
            timezone_expiration_date = self.utils.apply_timezone(invite.expires_at)
            embed.add_field(name="Date d'expiration", value=f"`{timezone_expiration_date.strftime('%d/%m/%Y %H:%M:%S')}` soit <t:{int(timezone_expiration_date.timestamp())}:R>", inline=False)

        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)

        # envoie du message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsInvite(bot))
