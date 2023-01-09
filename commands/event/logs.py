import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Logs(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    # === Message ===
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not self.utils.get_server_config(message.guild.id, "logs", "active"):
            return
        
        logs_channel = self.utils.get_server_config(message.guild.id, "logs", "channel_id")
        if logs_channel is None:
            return
        
        embed = discord.Embed(
            color=self.utils.embed_color()
        )
        embed.set_author(name=f"Message supprimé de {message.author.name}", icon_url=message.author.avatar.url)
        embed.add_field(name="Contenu", value=message.content, inline=False)


async def setup(bot):
    await bot.add_cog(Logs(bot))
