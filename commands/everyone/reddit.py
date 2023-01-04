from random import shuffle
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from asyncpraw import Reddit as RedditAPI

import config

class Reddit(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

        self.reddit_api = RedditAPI(
            client_id="3usCZAVHZYrTM8mbKK6_8Q",
            client_secret="mEmBiSuJFpaBCAioFOE1k4qk4wKlzQ",
            user_agent="Eula bot discord"
        )

    def UnixTimeToString(self, time: int) -> str:
        old = datetime.fromtimestamp(time)
        now = datetime.now()

        # la différence entre les deux dates, soit il y a combien de temps le post a été posté
        liste = [
            (now.year - old.year, "an"),
            (now.month - old.month, "mois"),
            (now.day - old.day, "jour"),
            (now.hour - old.hour, "heure"),
            (now.minute - old.minute, "minute"),
            (now.second - old.second, "seconde")
        ]

        res = "il y a " # on ajoute au string la première valeur positive
        for value, string in liste:
            if value > 0:
                res += f"{value} {string if value == 1 and string != 'mois' else string + 's'}"
                break

        return res

    async def reddit_command(self, ctx, subreddit: str, nombre: int):
        subreddit = subreddit.replace("r/", "")
        
        # si le commande a été executée avec un slash ctx.interaction != None
        if ctx.interaction is None:
            await ctx.message.add_reaction("<a:load:979084139200385024>")
        else:
            await ctx.interaction.response.defer()

        subreddit = await self.reddit_api.subreddit(subreddit)
        posts = subreddit.hot(limit=150)

        try:
            posts = [post async for post in posts if post.url.endswith((".jpg", ".png", ".jpeg", ".webp", ".jfif"))]
        except:
            await ctx.reply("Le subreddit n'existe pas", mention_author=False)
            return


        shuffle(posts)
        posts = posts[:nombre]

        # si le commande n'a pas été excutée avec un slash, on enleve l'emote
        if ctx.interaction is None:
            await ctx.message.clear_reaction("<a:load:979084139200385024>")

        for post in posts:
            embed = discord.Embed(title=post.title, url=post.shortlink, color=0xff4500)
            embed.set_image(url=post.url)
            embed.set_footer(text=f"r/{post.subreddit.display_name} | 👍 {post.score} | 💬 {post.num_comments} | 🕖 {self.UnixTimeToString(post.created_utc)}")
            await ctx.reply(embed=embed, mention_author=False)


    @commands.command()
    async def reddit(self, ctx: commands.Context, subreddit: str, nombre = "1"):
        nombre = int(nombre) if nombre.isdigit() else 1

        if nombre > 20 and ctx.author.id != config.owner_id:
            nombre = 20
            await ctx.send("Le nombre d'images ne peut pas dépasser 20")

        await self.reddit_command(ctx, subreddit, nombre)

    @reddit.error
    async def on_message_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Il manque des arguments\nsyntaxe: `reddit <subreddit> [nombre]`")


    @app_commands.command(name="reddit", description="envoie des images d'un subreddit")
    @app_commands.describe(subreddit="le subreddit")
    @app_commands.describe(nombre="le nombre d'images à envoyer")
    async def redditSlash(self, interaction: discord.Interaction, subreddit: str, nombre: app_commands.Range[int, 1, 20] = 1):
        ctx = await commands.Context.from_interaction(interaction)
        await self.reddit_command(ctx, subreddit, nombre)
    

    @commands.command(aliases=["randomreddit"])
    async def random_reddit(self, ctx, number = "1"):
        await self.reddit(ctx, self.reddit_api.random_subreddit(nsfw=True).__name__, number)


    @app_commands.command(name="random_reddit", description="envoie des images d'un subreddit aléatoire")
    @app_commands.describe(nombre="le nombre d'images à envoyer")
    async def random_redditSlash(self, interaction: discord.Interaction, nombre: app_commands.Range[int, 1, 20] = 1):
        ctx = await commands.Context.from_interaction(interaction)
        await self.reddit_command(ctx, self.reddit_api.random_subreddit(nsfw=True).__name__, nombre)


async def setup(bot):
    await bot.add_cog(Reddit(bot))
