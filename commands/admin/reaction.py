from asyncio import sleep as async_sleep

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Reaction(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    async def command(self, ctx: commands.Context, message: discord.Message, emojis: str):
        for i in range(len(emojis)):
            if emojis.find("><:", i) == i:
                emojis = emojis[:i + 1] + " " + emojis[i + 1:]

        for emojis in emojis.split(" "):
            await message.add_reaction(emojis)
        
        await ctx.reply("✅ Réactions ajoutées", mention_author=False)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reaction(self, ctx: commands.Context, message_link: str, *, emojis: str):
        message_link = message_link.split("/")

        channel_id = message_link[-2]
        message_id = message_link[-1]

        channel = await self.client.fetch_channel(channel_id)
        if channel is None or channel not in ctx.guild.channels:
            await ctx.send("Le salon est invalide")
            return

        message = await channel.fetch_message(message_id)
        if message is None:
            await ctx.send("Le message est invalide")
            return
        

        await self.command(ctx, message, emojis)


    @app_commands.command(name="reaction", description="ADMIN, Mets des réactions sur un message")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(message_link="le lien du message sur lequel réagir")
    @app_commands.describe(emojis="tous les emojis à ajouter au message séparés par des espaces")
    async def reactionSlash(self, interaction: discord.Interaction, message_link: str, emojis: str):
        ctx = await commands.Context.from_interaction(interaction)
        await interaction.response.defer()
        await self.reaction(ctx, message_link, emojis=emojis)


    @reaction.error
    async def reactionError(self, ctx, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await ctx.send(error_string)
        else:
            raise error


    @reactionSlash.error
    async def reactionSlashError(self, interaction, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await interaction.response.send_message(error_string, ephemeral=True)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Reaction(bot))
