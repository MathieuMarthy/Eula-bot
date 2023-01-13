from typing import Literal

import discord
from discord.ext import commands

from functions import Utils

class LogsVocal(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # Vérifications         
        if not self.utils.get_server_config(member.guild.id, "logs", "active"):
            return None
        
        logs_channel = self.utils.get_server_config(member.guild.id, "logs", "channel_id")
        logs_channel = self.client.get_channel(int(logs_channel))
        if logs_channel is None:
            return
        
        if before.channel == after.channel:
            return

        embed = discord.Embed(
            color=self.utils.embed_color()
        )

        # a rejoint un salon
        if before.channel is None and after.channel is not None:
            embed.set_author(name=f"{member.name} a rejoint un salon vocal", icon_url=member.avatar.url)
            embed.set_thumbnail(url=self.utils.get_img("enter"))
            embed.add_field(name="Salon rejoint", value=after.channel.mention)
        
        # a quitté un salon
        elif before.channel is not None and after.channel is None:
            embed.set_author(name=f"{member.name} a quitté un salon vocal", icon_url=member.avatar.url)
            embed.set_thumbnail(url=self.utils.get_img("exit"))
            embed.add_field(name="Salon quitté", value=before.channel.mention)
        
        # a changé de salon
        elif before.channel is not None and after.channel is not None:
            embed.set_author(name=f"{member.name} a changer de salon vocal", icon_url=member.avatar.url)
            embed.set_thumbnail(url=self.utils.get_img("shuffle"))
            embed.add_field(name="Ancien salon", value=before.channel.mention)
            embed.add_field(name="Nouveau salon", value=after.channel.mention)

        embed.add_field(name=self.utils.invisible_string(), value=member.mention + " - " + self.utils.get_date_time(), inline=False)

        # envoie le message
        await logs_channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LogsVocal(bot))
