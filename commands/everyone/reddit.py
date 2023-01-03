from random import shuffle

import discord
from discord import app_commands
from discord.ext import commands
from asyncpraw import Reddit as RedditAPI

class Reddit(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

        self.reddit_api = RedditAPI(
            client_id="3usCZAVHZYrTM8mbKK6_8Q",
            client_secret="mEmBiSuJFpaBCAioFOE1k4qk4wKlzQ",
            user_agent="Eula bot discord"
        )

    async def command(self, ctx, subreddit: str, nombre: int):
        subreddit = subreddit.replace("r/", "")
        
        if ctx.interaction is None:
            await ctx.message.add_reaction("<a:load:979084139200385024>")
        else:
            await ctx.interaction.response.defer()

        try:
            subreddit = await self.reddit_api.subreddit(subreddit)
            posts = subreddit.top(limit=150)
        except:
            await ctx.reply("Le subreddit n'existe pas", mention_author=False)
            return

        posts = [post async for post in posts if post.url.endswith((".jpg", ".png", ".gif", ".jpeg", ".gifv", ".mp4", ".webm"))]
        shuffle(posts)
        posts = posts[:nombre]
        
        if ctx.interaction is None:
            await ctx.message.clear_reaction("<a:load:979084139200385024>")

        for post in posts:
            await ctx.reply(post.url, mention_author=False)

    @commands.command()
    async def reddit(self, ctx, subreddit, nombre = "1"):
        nombre = int(nombre) if nombre.isdigit() else 1

        if nombre > 20:
            nombre = 20
            await ctx.send("Le nombre d'images ne peut pas dépasser 20")

        await self.command(ctx, subreddit, nombre)

    @reddit.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Il manque des arguments\nsyntaxe: `reddit <subreddit> [nombre]`")


    @app_commands.command(name="reddit", description="envoie des images d'un subreddit")
    @app_commands.describe(subreddit="le subreddit")
    @app_commands.describe(nombre="le nombre d'images à envoyer")
    async def redditSlash(self, interaction: discord.Interaction, subreddit: str, nombre: app_commands.Range[int, 1, 20] = 1):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, subreddit, nombre)


async def setup(bot):
    await bot.add_cog(Reddit(bot))
