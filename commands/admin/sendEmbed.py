import json as jsonlib

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class SendEmbed(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)

    async def command(self, ctx: commands.Context, channel: discord.TextChannel, json: str):
        if ctx.interaction is not None:
            await ctx.interaction.response.defer()

        try:
            json = jsonlib.loads(json)
        except jsonlib.decoder.JSONDecodeError:
            await ctx.send("Le json est invalide")
            return

        embeds = []
        for json_embed in json["embeds"]:
            try:
                embeds.append(discord.Embed.from_dict(json_embed))
            except discord.errors.HTTPException as e:
                await ctx.send(f"Une erreur est survenue avec l'embed \"{json_embed['title']}\":\n`{e}`")
                return

        for embed in embeds:
            try:
                await channel.send(embed=embed)
            except discord.errors.HTTPException as e:
                await ctx.send(f"Une erreur est survenue avec l'embed \"{embed.title}\":\n`{e}`")
        
        await ctx.reply(f"Embed{'s' if len(embeds) > 1 else ''} envoyé", mention_author=False)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def send_embed(self, ctx, channel, *, json: str):
        channel = channel.replace("<", "").replace("#", "").replace(">", "")
        channel = await self.client.fetch_channel(channel)

        if channel is None:
            await ctx.send("Le salon est invalide")
            return

        await self.command(ctx, channel, json)


    @app_commands.command(name="send_embed", description="Envoie un embed dans un salon")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="le salon dans lequel envoyer l'embed")
    @app_commands.describe(json="le json contenant les informations de l'embed, faites /help_send_embed pour plus d'informations")
    async def send_embedSlash(self, interaction: discord.Interaction, channel: discord.TextChannel, json: str):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, channel, json)


    async def help_send_embed_command(self, ctx: commands.Context):
        json = \
        """
        ```json
        {
            "embeds": [{
                "title": "Hello!",
                "color": 1127128,
                "description": "Hi! :grinning:",
                "author": {
                    "name": "Delivery Girl",
                    "url": "https://www.reddit.com/r/Pizza/",
                    "icon_url": "https://i.imgur.com/V8ZjaMa.jpg"
                },
                "url": "https://google.com/",
                "fields": [
                    {
                        "name": "Cat",
                        "value": "Hi! :wave:",
                        "inline": true
                    },
                    {
                        "name": "Dog",
                        "value": "hello!",
                        "inline": true
                    }
                ],
                "image": {
                    "url": "https://i.imgur.com/ZGPxFN2.jpg"
                },
                "thumbnail": {
                    "url": "https://upload.wikimedia.org/wikipedia/commons/3/38/4-Nature-Wallpapers-2014-1_ukaavUI.jpg"
                },
                "footer": {
                    "text": "Woah! *So cool!* :smirk:",
                    "icon_url": "https://i.imgur.com/fKL31aD.jpg"
                },
                "timestamp": "2015-12-31T12:00:00.000Z"
            }]
        }
        ```
        """
        await ctx.send(f"Le format du json est le suivant : \n{json}")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def help_send_embed(self, ctx):
        await self.help_send_embed_command(ctx)


    @app_commands.command(name="help_send_embed", description="envoi un message d'aide pour la commande send_embed")
    @app_commands.checks.has_permissions(administrator=True)
    async def help_send_embedSlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.help_send_embed_command(ctx)
    

    @help_send_embed.error
    async def help_send_embedError(self, ctx, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await ctx.send(error_string)


    @help_send_embedSlash.error
    async def help_send_embedSlashError(self, interaction, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await interaction.response.send_message(error_string, ephemeral=True)


async def setup(bot):
    await bot.add_cog(SendEmbed(bot))
