import random

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Chat(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)

        self.links_hello = [
            "https://c.tenor.com/thNxDWlG1EcAAAAC/killua-zoldyck-anime.gif",
            "https://media.giphy.com/media/yyVph7ANKftIs/giphy.gif",
            "https://c.tenor.com/OSnZnnqx4vsAAAAC/anime-hello.gif",
            "https://c.tenor.com/WcJoZqd4C_YAAAAC/eromanga-sensei-anime.gif",
            "https://c.tenor.com/mjwiXPyqyrgAAAAC/hello-hi.gif",
            "https://c.tenor.com/dKv5A-KGZsIAAAAC/shy-hi.gif",
            "https://c.tenor.com/Q1dW7INg5ioAAAAC/hello-anime.gif",
            "https://c.tenor.com/cDCkQ6BPlF4AAAAC/pat-pat-anime.gif",
            "https://c.tenor.com/zeJzW4ubYqkAAAAC/nasuno-cat.gif",
            "https://c.tenor.com/6Gr-6QEvE7EAAAAd/school-live-cute.gif",
            "https://c.tenor.com/3g3D1mECft0AAAAC/anime-hi.gif",
            "https://c.tenor.com/dCTUyNt499gAAAAC/kobayashi-dragon.gif",
            "https://c.tenor.com/Z2-F9Bdaa9QAAAAC/anime-girl.gif",
            "https://c.tenor.com/g0QIOyhPLRQAAAAC/neon_cove-cute.gif"
        ]

        self.links_kiss = [
            "https://www.icegif.com/wp-content/uploads/anime-kiss-icegif-1.gif",
            "https://c.tenor.com/F02Ep3b2jJgAAAAC/cute-kawai.gif",
            "https://c.tenor.com/g9HjxRZM2C8AAAAd/anime-love.gif",
            "https://c.tenor.com/nRdyrvS3qa4AAAAC/anime-kiss.gif",
            "https://c.tenor.com/vhuon7swiOYAAAAC/rakudai-kishi-kiss.gif",
            "https://c.tenor.com/5iiiF4A7KI0AAAAC/anime-cry-anime.gif",
            "https://c.tenor.com/2u67zOB43esAAAAd/cute-anime.gif",
            "https://c.tenor.com/DDmZqcOZJisAAAAC/anime.gif",
            "https://c.tenor.com/G954PGQ7OX8AAAAd/cute-urara-shiraishi-anime.gif",
            "https://c.tenor.com/kyM-QWHWy1cAAAAC/anime-kissing.gif",
            "https://c.tenor.com/7T1cuiOtJvQAAAAC/anime-kiss.gif",
            "https://c.tenor.com/BJ9v5r4Th7UAAAAC/love-couple.gif"
        ]

        self.links_pat = [
            "https://c.tenor.com/TDqVQaQWcFMAAAAC/anime-pat.gif",
            "https://c.tenor.com/Av63tpT8Y14AAAAC/pat-head.gif",
            "https://c.tenor.com/2vFAxyl6cI8AAAAd/mai-headpats.gif",
            "https://c.tenor.com/6dyxfdQx--AAAAAd/anime-senko-san.gif",
            "https://c.tenor.com/g75K3KA3VeAAAAAd/anime-sleep.gif",
            "https://c.tenor.com/OUSrLXimAq8AAAAC/head-pat-anime.gif",
            "https://c.tenor.com/zBPha3hhm7QAAAAC/anime-girl.gif",
            "https://c.tenor.com/N41zKEDABuUAAAAC/anime-head-pat-anime-pat.gif",
            "https://c.tenor.com/E6fMkQRZBdIAAAAC/kanna-kamui-pat.gif",
            "https://c.tenor.com/n6M5-pM2RiQAAAAC/anime-cry.gif",
            "https://c.tenor.com/edHuxNBD6IMAAAAC/anime-head-pat.gif",
            "https://c.tenor.com/i7nXGbPLqTsAAAAC/anime-hug.gif",
            "https://c.tenor.com/1bBIALbG0ikAAAAC/anime-anime-head-rub.gif",
            "https://c.tenor.com/lnoDyTqMk24AAAAC/anime-anime-headrub.gif",
            "https://c.tenor.com/sX-K9XVf6KoAAAAC/catgirl-neko.gif",
            "https://c.tenor.com/9R7fzXGeRe8AAAAC/fantasista-doll-anime.gif",
            "https://c.tenor.com/G14pV-tr0NAAAAAC/anime-head.gif",
            "https://c.tenor.com/epo_ns_GbwoAAAAC/anime-head-pat.gif"
        ]

        self.links_hug = [
            "https://c.tenor.com/QTbBCR3j-vYAAAAd/hugs-best-friends.gif",
            "https://c.tenor.com/8Jk1ueYnyYUAAAAC/hug.gif",
            "https://c.tenor.com/-3I0yCd6L6AAAAAC/anime-hug-anime.gif",
            "https://c.tenor.com/0T3_4tv71-kAAAAC/anime-happy.gif",
            "https://c.tenor.com/QwHSis0hNEQAAAAC/love-hug.gif",
            "https://c.tenor.com/9e1aE_xBLCsAAAAC/anime-hug.gif",
            "https://c.tenor.com/we1trpFB2F0AAAAC/neko-hug.gif",
            "https://c.tenor.com/2lr9uM5JmPQAAAAC/hug-anime-hug.gif",
            "https://c.tenor.com/4n3T2I239q8AAAAC/anime-cute.gif",
            "https://c.tenor.com/0vl21YIsGvgAAAAC/hug-anime.gif",
            "https://c.tenor.com/gqM9rl1GKu8AAAAC/kitsune-upload-hug.gif",
            "https://c.tenor.com/arMxz72tc50AAAAC/catgirl-hug.gif",
            "https://c.tenor.com/keasv-Cnh4kAAAAd/hug-cuddle.gif",
            "https://c.tenor.com/ggKei4ayfIAAAAAC/anime-hug.gif",
            "https://c.tenor.com/e4xYciCG6NcAAAAM/emdj-snuggle.gif",
            "https://c.tenor.com/aG0pA87t0dMAAAAC/anime-chino.gif",
            "https://c.tenor.com/1PSvBKNcNtUAAAAC/love-anime.gif"
        ]

        self.links_baka = [
            "https://c.tenor.com/UsggMuRixo0AAAAC/baka-anime.gif",
            "https://c.tenor.com/dJpiway_niUAAAAC/onichan-baka-onichan.gif",
            "https://c.tenor.com/Xcr8fHyf84gAAAAC/baka-anime.gif",
            "https://c.tenor.com/pHCT4ynbGIUAAAAC/anime-girl.gif",
            "https://c.tenor.com/ESvZeEc2lIQAAAAC/baka-anime.gif",
            "https://c.tenor.com/bNrnl6bi8BEAAAAC/anime-bleh.gif",
            "https://c.tenor.com/2An5JdBiT9YAAAAC/baka-anime.gif",
            "https://c.tenor.com/ggjmRnG_oBAAAAAC/anime-baka.gif",
            "https://c.tenor.com/XcKQzqJPiGcAAAAC/anime-tsundere.gif",
            "https://c.tenor.com/dHZOfR6rZY0AAAAC/baka-anime.gif",
            "https://c.tenor.com/Ytn7KcbZm8wAAAAM/baka-anime.gif",
            "https://c.tenor.com/smRK3hdF5DMAAAAC/baka-anime.gif",
            "https://c.tenor.com/1IDzm1044LQAAAAC/baka-anime.gif",
            "https://c.tenor.com/icCAaeNx5UAAAAAC/zasbaka.gif"
        ]

        self.links_bite = [
            "https://c.tenor.com/IKDf1NMrzsIAAAAC/anime-acchi-kocchi.gif",
            "https://c.tenor.com/MKjNSLL4dGoAAAAC/bite-cute.gif",
            "https://c.tenor.com/4j3hMz-dUz0AAAAC/anime-love.gif",
            "https://c.tenor.com/MNK1CrjgMcMAAAAC/megumin-konosuba.gif",
            "https://c.tenor.com/6HhJw-4zmQUAAAAC/anime-bite.gif",
            "https://c.tenor.com/mXc2f5NeOpgAAAAC/no-blood-neck-bite.gif",
            "https://c.tenor.com/aKzAQ_cFsFEAAAAC/arms-bite.gif",
            "https://c.tenor.com/xAiGlpwEVhEAAAAC/josee-josee-to-tora-to-sakanatachi.gif",
            "https://c.tenor.com/TwP8Vv8acSkAAAAC/the-melancholy-of-haruhi-suzumiya-biting-ear.gif",
            "https://c.tenor.com/TX6YHUnHJk4AAAAC/mao-amatsuka-gj-bu.gif",
            "https://c.tenor.com/8UjO54apiUIAAAAC/gjbu-bite.gif",
            "https://c.tenor.com/BVFbvCZKNEsAAAAC/princess-connect-anime-bite.gif",
            "https://c.tenor.com/Xpv7HTk-DIYAAAAC/mad-angry.gif",
            "https://c.tenor.com/vHfD8O5dDd4AAAAC/acchi-kocchi-anime.gif",
            "https://c.tenor.com/Nk-Eq8_ZiNwAAAAC/index-toaru.gif",
            "https://c.tenor.com/DBwz1nSElowAAAAC/aruu-anime.gif",
            "https://c.tenor.com/0kjdOr9jyN0AAAAC/bite-girl.gif",
            "https://c.tenor.com/sRPSPdWp9zsAAAAC/one-piece-anime.gif",
            "https://c.tenor.com/ZS2uG_TqqDwAAAAC/bite.gif"
        ]


    async def command(self, ctx, liens, msg):
        embed = discord.Embed(title=msg, description="󠀮 ", color=self.utils.embed_color())
        embed.set_image(url=random.choice(liens))
        await ctx.send(embed=embed)


    @commands.command(aliases=["hello"])
    async def bonjour(self, ctx, member):
        member = self.utils.get_member(member)
        if member is None:
            await ctx.send("Utilisateur introuvable")
            return

        await self.command(ctx, self.links_hello, f"{ctx.author.name} dit bonjour à {member.name} !")


    @app_commands.command(name="bonjour", description="dit bonjour à quelqu'un !")
    @app_commands.describe(personne="la personne à qui tu veux dire bonjour !")
    async def bonjourSlash(self, interaction: discord.Interaction, personne: discord.Member):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, self.links_hello, f"{interaction.user.name} dit bonjour à {personne.name} !")


    @commands.command(aliases=["bite"])
    async def mord(self, ctx, member):
        member = self.utils.get_member(member)
        if member is None:
            await ctx.send("Utilisateur introuvable")
            return

        await self.command(ctx, self.links_bite, f"{ctx.author.name} mord {member.name}")


    @app_commands.command(name="mord", description="mords quelqu'un !")
    @app_commands.describe(personne="la personne que tu veux mordre !")
    async def mordSlash(self, interaction: discord.Interaction, personne: discord.Member):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, self.links_bite, f"{interaction.user.name} mord {personne.name} !")
    

    @commands.command(aliases=["kiss"])
    async def bisous(self, ctx, member):
        member = self.utils.get_member(member)
        if member is None:
            await ctx.send("Utilisateur introuvable")
            return

        await self.command(ctx, self.links_kiss, f"{ctx.author.name} fait un bisous à {member.name} <3")


    @app_commands.command(name="bisous", description="fait un bisous à quelqu'un !")
    @app_commands.describe(personne="l'élu de ton coeur !")
    async def bisousSlash(self, interaction: discord.Interaction, personne: discord.Member):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, self.links_kiss, f"{interaction.user.name} fait un bisous à {personne.name} <3")
    

    @commands.command(aliases=["pat"])
    async def tapoter(self, ctx, member):
        member = self.utils.get_member(member)
        if member is None:
            await ctx.send("Utilisateur introuvable")
            return

        await self.command(ctx, self.links_pat, f"{ctx.author.name} tapote la tête de {member.name}")


    @app_commands.command(name="tapoter", description="*pat pat*")
    @app_commands.describe(personne="la personne à qui tu veux tapoter la tête !")
    async def tapoterSlash(self, interaction: discord.Interaction, personne: discord.Member):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, self.links_pat, f"{interaction.user.name} tapote la tête de {personne.name}")
    

    @commands.command(aliases=["hug"])
    async def calin(self, ctx, member):
        member = self.utils.get_member(member)
        if member is None:
            await ctx.send("Utilisateur introuvable")
            return

        await self.command(ctx, self.links_hug, f"{ctx.author.name} fait un calin à {member.name}")


    @app_commands.command(name="calin", description="🤗")
    @app_commands.describe(personne="la personne que tu veux serrer dans tes bras !")
    async def calinSlash(self, interaction: discord.Interaction, personne: discord.Member):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, self.links_hug, f"{interaction.user.name} fait un calin à {personne.name}")
    

    @commands.command()
    async def baka(self, ctx, member):
        member = self.utils.get_member(member)
        if member is None:
            await ctx.send("Utilisateur introuvable")
            return

        await self.command(ctx, self.links_baka, f"{member.name} est trop un ba..baka ! ૮₍ ˃ ⤙ ˂ ₎ა")


    @app_commands.command(name="baka", description="ba...baka !")
    @app_commands.describe(personne="un baka")
    async def bakaSlash(self, interaction: discord.Interaction, personne: discord.Member):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, self.links_baka, f"{personne.name} est trop un ba..baka ! ૮₍ ˃ ⤙ ˂ ₎ა")


async def setup(bot):
    await bot.add_cog(Chat(bot))
