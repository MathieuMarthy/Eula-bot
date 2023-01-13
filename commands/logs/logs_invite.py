from typing import Literal

import discord
from discord.ext import commands

from functions import Utils

class LogsInvite(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    def create_embed(self, invite: discord.Invite, type: Literal["create", "delete"]) -> discord.Embed:
        title = "Une invitation à été "
        if type == "create":
            title += "créée"
            image = "add"
        elif type == "delete":
            title += "supprimée"
            image = "trash"

       # création de la base de l'embed
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=title, icon_url=self.utils.get_img("setting"))
        embed.set_thumbnail(url=self.utils.get_img(image))

        embed.add_field(name="Invitation", value=invite.url, inline=True)
        embed.add_field(name="Créateur", value=invite.inviter.mention, inline=True)

        if invite.expires_at is not None:
            timezone_expiration_date = self.utils.apply_timezone(invite.expires_at)
            embed.add_field(name="Date d'expiration", value=f"`{timezone_expiration_date.strftime('%d/%m/%Y %H:%M:%S')}` soit <t:{int(timezone_expiration_date.timestamp())}:R>", inline=False)


        embed.add_field(name="Nombre d'utilisations", value=f"`{'illimité' if invite.max_uses == 0 else invite.max_uses}`", inline=True)

        embed.add_field(name=self.utils.invisible_string(), value=self.utils.get_date_time(), inline=False)
        return embed


    def checks(self, invite: discord.Invite) -> discord.TextChannel:
        # Vérifications         
        if not self.utils.get_server_config(invite.guild.id, "logs", "active"):
            return None
        
        logs_channel = self.utils.get_server_config(invite.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))

        if invite.scheduled_event is not None:
            return None

        return logs_channel


    # === Invite ===
    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        logs_channel = self.checks(invite)
        if logs_channel is None:
            return

        embed = self.create_embed(invite, "create")

        # envoie du message
        await logs_channel.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        logs_channel = self.checks(invite)
        if logs_channel is None:
            return

        embed = self.create_embed(invite, "delete")

        # envoie du message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsInvite(bot))
