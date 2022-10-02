import asyncio
import ast
import os
import random
from zoneinfo import ZoneInfo
import requests
from datetime import datetime
import json

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext import tasks
from asyncpraw import Reddit

from image import get_img
from randomizer import randomizer_image

# --- setup
reddit = Reddit(
    client_id="3usCZAVHZYrTM8mbKK6_8Q",
    client_secret="mEmBiSuJFpaBCAioFOE1k4qk4wKlzQ",
    user_agent="Eula bot discord"
)
token = "OTE0MjI2MzkzNTY1NDk5NDEy.YaJ9rQ.YHLkLmSADNTjtztiWBuMMSi4g8A"
path = os.path.dirname(os.path.abspath(__file__))
prefix = "!"
version_bot = "4.0.8"
changelog = "**rand**\non peut mettre le nom d'un champion"
default_intents = discord.Intents.default().all()
default_intents.members = True
client = commands.Bot(
    command_prefix=[prefix, "<@914226393565499412> ", "<@914226393565499412>", "<@!914226393565499412> ",
                    "<@!914226393565499412>"], help_command=None, intents=default_intents)
dico_activity = json.load(open(os.path.join(path, "activities.json"), "r"))
dico_activity = {int(k): v for k, v in dico_activity.items()}
month_file = open(os.path.join(path, "month.txt")).read()
loop_counter_month = 0

# --- dico
dico = ast.literal_eval(open(os.path.join(path, "server.txt"), "r").read().replace("b'", "'").replace("'", '"'))
# forme:  {id: {"name": str, "logs": int, "voc": int, "autorole": int, "welcome_msg": str}}

print("connection...")


def utf8(string: str) -> str:
    return string.encode("utf-8")


@client.event
async def on_ready():
    global status
    print(f"connecté ! ⊂(◉‿◉)つ à {client.user.name}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"{prefix}help"))

    for serveur in client.guilds:
        if serveur.id not in dico:
            dico[serveur.id] = {"name": utf8(serveur.name), "logs": None, "voc": None, "autorole": None}
        elif utf8(serveur.name) != utf8(dico[serveur.id]["name"]):
            dico[serveur.id]["name"] = utf8(serveur.name)

    tmp = [server.id for server in client.guilds]
    for server, _ in dico.copy().items():
        if server not in tmp:
            del dico[server]

    dico_update()
    loop.start()


# --- fonctions
# - loop
@tasks.loop(seconds=60)
async def loop():
    global dico_activity, month_file, loop_counter_month

    loop_counter_month += 1
    if loop_counter_month >= 5:
        loop_counter_month = 0

        actual_month = str(datetime.today().month)
        if month_file != actual_month:
            month_file = actual_month

            open(os.path.join(path, "month.txt"), "w").write(str(actual_month))
            dico_activity = {}

    for server in client.guilds:

        dico_activity[server.id] = dico_activity.get(server.id, {})
        for member in server.members:

            if member.activities is not None and not member.bot:

                for activity in member.activities:
                    if activity.type == discord.ActivityType.playing:

                        dico_activity[server.id][activity.name] = dico_activity[server.id].get(activity.name, 0) + 1

    json.dump(dico_activity, open(os.path.join(path, "activities.json"), "w"))


# - all
def dico_update():
    open(os.path.join(path, "server.txt"), "w").write(str(dico))


def channel_send(id):
    return client.get_channel(id)


def get_date_time():
    return datetime.now(tz=ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y %H:%M:%S")


def replaces(string, *args):
    for i in range(0, len(args), 2):
        string = string.replace(args[i], args[i + 1])
    return string


def get_member(member):
    if member is None:
        return None
    if not member.isdigit():
        if "!" in member:
            member = replaces(member, "<@!", "", ">", "")
        else:
            member = replaces(member, "<@", "", ">", "")
    return client.get_user(int(member))


async def check_permissions(ctx):
    guild = ctx.guild
    role_vocal = guild.get_role(dico[guild.id]["voc"])
    role_autorole = guild.get_role(dico[guild.id]["autorole"])
    role_eula = discord.utils.get(guild.roles, name="Eula")

    guild_roles_id = [role.id for role in guild.roles]

    for role in [role_vocal, role_autorole]:
        if guild_roles_id.index(role_eula.id) < guild_roles_id.index(role.id):
            await ctx.send(f"Le role Eula doit être plus haut que le rôle {role.name}")
    


# - mini jeux
async def start_game_multi(ctx, limit, name_game):
    """
    Args:
    -----
        ctx : ctx
        limit : le nombre de manches dans le jeu
        name_game : nom du jeu

    return:
    -------
        list : liste des participants
        dict : dictionnaire des points 

    """
    if str(limit).isdigit():
        limit = int(limit)
    else:
        limit = 5
    msg = await ctx.send(f"**Partie de {name_game} lancée !**\npour participer réagissez avec 🖐️")
    await msg.add_reaction("🖐️")
    await asyncio.sleep(15)
    list_user = []

    async for e in ctx.channel.history(limit=100):
        if e.id == msg.id:
            for reaction_of_message in e.reactions:
                if reaction_of_message.emoji == "🖐️":
                    async for user in reaction_of_message.users():
                        if user.id != client.user.id:
                            list_user.append(user)
            break

    if len(list_user) == 0:
        await ctx.reply("Aucun joueur n'a rejoint la partie", mention_author=False)
        return [], []

    str_name = ""
    dico_points = {}

    for i in list_user:
        dico_points[i.id] = 0
        str_name += ", " + i.name

    str_name = str_name.replace(", ", "", 1)
    await ctx.send(f"Liste des participants: {str_name}\nC'est parti pour {limit} manches !")
    await asyncio.sleep(3)
    return list_user, dico_points


async def start_game_duo(ctx, member, name_game):
    member = get_member(member)

    if member is None:
        await ctx.send("Vous n'avez pas mentionné un joueur")
        return False, None

    await ctx.send(f"{member.mention} acceptez-vous la partie de {name_game} contre **{ctx.author.name}** ?")
    try:
        msg = await client.wait_for("message", check=lambda message: message.author.id in [member.id,
                                                                                           ctx.author.id] and message.content.lower() in [
                                                                         "y", "o", "n", "yes", "oui", "no", "non"],
                                    timeout=180)
    except asyncio.TimeoutError:
        await ctx.reply(f"**{member.name}** n'a pas répondu", mention_author=False)
        return False, None

    if msg.content.lower() in ["n", "non", "no"]:
        await ctx.send("Partie refusée")
        return False, None

    else:
        return True, member


async def end_game(ctx, list_user, dico_points):
    """
    Args:
    -----
        ctx : ctx
        list_user : liste de tous les participants
        dico_points : dictionnaire des points 
    """
    n = (list_user[0].id, dico_points[list_user[0].id])

    for id, point in dico_points.items():
        if n[1] < point:
            n = (id, point)

    list_winner = [id for id, point in dico_points.items() if n[1] == point]
    if len(list_winner) == 1:
        username = client.get_user(list_winner[0])
        await ctx.send(
            f"󠀮 \n**Partie finie !**\nLe vainqueur est {username.mention} avec {dico_points[username.id]} points !")
    else:
        str_winner = ""
        for i, e in enumerate(list_winner):
            username = client.get_user(list_winner[i])
            str_winner += " " + username.mention
        await ctx.send(
            f"󠀮 \n**Partie finie !**\nLes vainqueurs sont {str_winner} avec {dico_points[username.id]} points !")


# --- commandes/commands
# - everyone
@client.command(aliases=["rand"])
async def randomizer(ctx, option="random"):
    if option.isdigit():
        option = int(option)
        if option <= 0 or option > 5:
            await ctx.reply("Le nombre doit être entre 1 et 5\n1 -> top\n2 -> jungle\n3 -> mid\n4 -> adc\n5 -> support",
                            mention_author=False)
            return

    elif option == "team":
        role = [1, 2, 3, 4, 5]
        random.shuffle(role)
        for _ in range(5):
            image_path = randomizer_image(role[0])
            role.pop(0)
            with open(image_path, "rb") as f:
                image = discord.File(f)
                await ctx.reply(file=image, mention_author=False)
            os.remove(image_path)
            await asyncio.sleep(0.1)
        return
    

    image_path = randomizer_image(option)
    with open(image_path, "rb") as f:
        image = discord.File(f)
        await ctx.reply(file=image, mention_author=False)
    os.remove(image_path)
 

@client.command()
async def top(ctx, nbr=5):
    tmp = sorted(dico_activity[ctx.guild.id].items(), key=lambda x: x[1], reverse=True)
    if len(tmp) > nbr:
        tmp = tmp[:nbr]
    tmp = [f"{k} : {divmod(v, 60)[0]}h {v % 60}min" for k, v in tmp]

    embed = discord.Embed(title=f"Top {len(tmp)} des activités du mois", description="\n".join(tmp), color=0xf0a3ff)
    await ctx.send(embed=embed)


async def message_tag(ctx, liens, msg):
    embed = discord.Embed(title=msg, description="󠀮 ", color=0x555555)
    embed.set_image(url=random.choice(liens))
    await ctx.send(embed=embed)


@client.command(aliases=["hello", "hi"])
async def bonjour(ctx, member=None):
    member = get_member(member)
    if member is None:
        await ctx.send("Vous n'avez pas mentionné un joueur")
        return

    liste_liens = ["https://c.tenor.com/thNxDWlG1EcAAAAC/killua-zoldyck-anime.gif",
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
                   "https://c.tenor.com/g0QIOyhPLRQAAAAC/neon_cove-cute.gif"]
    await message_tag(ctx, liste_liens, f"{ctx.author.name} dit bonjour à {member.name} !")


@client.command(aliases=["kiss"])
async def bisous(ctx, member=None):
    member = get_member(member)
    if member is None:
        await ctx.send("Vous n'avez pas mentionné un joueur")
        return

    liste_liens = ["https://www.icegif.com/wp-content/uploads/anime-kiss-icegif-1.gif",
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
                   "https://c.tenor.com/BJ9v5r4Th7UAAAAC/love-couple.gif"]
    await message_tag(ctx, liste_liens, f"{ctx.author.name} embrasse {member.name} !")


@client.command()
async def pat(ctx, member=None):
    member = get_member(member)
    if member is None:
        await ctx.send("Vous n'avez pas mentionné un joueur")
        return

    liste_liens = ["https://c.tenor.com/TDqVQaQWcFMAAAAC/anime-pat.gif",
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
                   "https://c.tenor.com/epo_ns_GbwoAAAAC/anime-head-pat.gif"]
    await message_tag(ctx, liste_liens, f"{ctx.author.name} pat {member.name} !")


@client.command(aliases=["calin"])
async def hug(ctx, member=None):
    member = get_member(member)
    if member is None:
        await ctx.send("Vous n'avez pas mentionné un joueur")
        return

    liste_liens = ["https://c.tenor.com/QTbBCR3j-vYAAAAd/hugs-best-friends.gif",
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
                   "https://c.tenor.com/1PSvBKNcNtUAAAAC/love-anime.gif"]
    await message_tag(ctx, liste_liens, f"{ctx.author.name} fait un calin {member.name} !")


@client.command()
async def baka(ctx, member=None):
    member = get_member(member)
    if member is None:
        await ctx.send("Vous n'avez pas mentionné un joueur")
        return

    liste_liens = ["https://c.tenor.com/UsggMuRixo0AAAAC/baka-anime.gif",
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
                   "https://c.tenor.com/icCAaeNx5UAAAAAC/zasbaka.gif"]
    await message_tag(ctx, liste_liens, f"{member.name} est trop un baka !")


@client.command(aliases=["mange", "mords", "mord"])
async def bite(ctx, member=None):
    member = get_member(member)
    if member is None:
        await ctx.send("Vous n'avez pas mentionné un joueur")
        return

    liste_liens = ["https://c.tenor.com/IKDf1NMrzsIAAAAC/anime-acchi-kocchi.gif",
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
                   "https://c.tenor.com/ZS2uG_TqqDwAAAAC/bite.gif", ""]
    await message_tag(ctx, liste_liens, f"{ctx.author.name} mord {member.name}")


@client.command(aliases=["reddit"])
async def redditt(ctx, subreddit, nbr="1", option="None"):
    if nbr.isdigit():
        nbr = int(nbr)
    else:
        nbr = 1

    if nbr > 20 and option != "cheat":
        await ctx.send("Le nombre maximum d'images est de 20")
        nbr = 20

    subreddit = subreddit.replace("r/", "")
    await ctx.message.add_reaction("<a:load:979084139200385024>")

    links = []
    try:
        reddit_posts = await reddit.subreddit(subreddit)
        posts = [post async for post in reddit_posts.hot(limit=200) if
                 post.url.endswith((".jpg", ".png", ".gif", ".jpeg", ".gifv", ".mp4", ".webm"))]
    except:
        await ctx.message.clear_reaction("<a:load:979084139200385024>")
        await ctx.reply("Le subreddit n'existe pas\nLe subreddit doit être écrit exactement pareil que sur reddit",
                        mention_author=False)
        return

    while len(links) < nbr:
        if len(posts) == 0:
            break
        post = posts.pop(random.randint(0, len(posts) - 1))
        links.append(post.url)

    await ctx.message.clear_reaction("<a:load:979084139200385024>")

    if len(links) == 0:
        await ctx.reply("Aucune image dans le subreddit", mention_author=False)
        return

    for link in links:
        await ctx.reply(link, mention_author=False)


@redditt.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque le subreddit  ! syntaxe: {prefix}reddit <subreddit> <#nombre d'images>")


@client.command()
async def version(ctx):
    embed = discord.Embed(color=0xf0a3ff, title="Version - Changelog", description=f"**Version:** {version_bot}\n\nChangelog:\n\n{changelog}")
    await ctx.send(embed=embed)


@client.command()
async def hentai(ctx, category="help", nbr="1"):
    if not ctx.channel.is_nsfw() and not ctx.author.guild_permissions.administrator:
        await ctx.send("Il faut que le salon soit nsfw pour que la commande fonctionne")
        return

    if nbr.isdigit():
        nbr = int(nbr)
    else:
        nbr = 1

    if nbr > 20:
        await ctx.send("Le nombre maximum d'images est de 20")
        nbr = 20

    tags = ["ass", "bdsm", "cum", "creampie", "manga", "femdom", "hentai", "incest", "masturbation", "public", "ero",
            "orgy", "elves", "yuri", "pantsu", "glasses", "cuckold", "blowjob", "boobjob", "foot", "thighs", "vagina",
            "ahegao", "uniform", "gangbang", "tentacles", "gif", "neko", "nsfwMobileWallpaper", "zettaiRyouiki"]
    if category in tags:
        for _ in range(nbr):
            response = requests.get(f"https://hmtai.herokuapp.com/nsfw/{category}")
            link = ast.literal_eval(response.text)
            await ctx.send(link["url"])
    else:
        await ctx.send(f"**Liste des categories:**\n{', '.join(tags)}")


@client.command(aliases=["profile_picture", "pdp"])
async def pp(ctx, member):
    if member in ["serveur", "server"]:
        filename = "avatar.gif" if ctx.message.guild.is_icon_animated() else "avatar.png"
        await ctx.message.guild.icon_url.save(filename)

    else:
        member = get_member(member)
        if member is None:
            await ctx.send("Vous n'avez pas mentionné un membre !")
            return

        else:
            filename = "avatar.gif" if member.is_avatar_animated() else "avatar.png"
            await member.avatar_url.save(filename)

    file = discord.File(fp=filename)
    await ctx.send(file=file)
    os.remove(filename)


@pp.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque le membre ! syntaxe: {prefix}pp <id du membre/mention>")


@client.command(aliases=["random"])
async def aleatoire(ctx, nbr):
    if int(nbr) < 0:
        await ctx.send("Le nombre doit être plus grand que 0")
    else:
        await ctx.send(random.randint(0, int(nbr)))


@aleatoire.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque le nombre ! syntaxe: {prefix}random <nombre>")


@client.command(aliases=["pile", "face", "piece", "pileouface"])
async def pile_ou_face(ctx):
    embed = discord.Embed(color=0xf0a3ff)

    if random.choice([True, False]):
        embed.add_field(name=f"󠀮Pile", value="----", inline=True)
        embed.set_image(url=get_img("pile"))
    else:
        embed.add_field(name=f"󠀮Face", value="----", inline=True)
        embed.set_image(url=get_img("face"))

    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=["8ball", "8"])
async def eightball(ctx, *, msg):
    a = ["Une chance sur deux", "D'après moi oui", "C'est certain", "Oui absolument", "Sans aucun doute",
         "Très probable", "Oui", "C'est bien parti", "C'est non", "Peu probable", "Faut pas rêver", "N'y compte pas",
         "Impossible"]
    if msg.endswith("ratio ?"):
        await ctx.reply("ratio !", mention_author=False)
    else:
        await ctx.reply(random.choice(a), mention_author=False)


@client.command()
async def ping(ctx):
    embed = discord.Embed(color=0xf0a3ff)
    embed.set_author(name="ping", icon_url=client.user.avatar_url)
    embed.set_thumbnail(url=get_img("power"))
    embed.add_field(name="󠀮 ", value="**Je suis connecté !**", inline=True)
    await ctx.send(embed=embed)


@client.command()
async def help(ctx):
    liste_emoji = [
        "🏠",
        "👑",
        "🎮",
        "🔧",
        "📝",
        "💬"
    ]

    dico_help = {
        "🏠": {
            "🏠 - Accueil": "󠀮 ",
            "👑 - Admin": "󠀮 ",
            "🎮 - Jeux": "󠀮 ",
            "🔧 - Utilitaire": "󠀮 ",
            "📝 - General": "󠀮 ",
            "💬 - Chat": "󠀮 "
        },

        "👑": {
            f"{prefix}toggle_autorole <role>": "active/désactive le fait de donner un rôle a tous les nouveaux arrivant",
            f"{prefix}toggle_rolevocal": "active/désactive le fait de donner un rôle à chaque fois qu'un membre rejoint un salon vocal",
            f"{prefix}toggle_logs": "active/désactive les logs",
            f"{prefix}toggle_welcome_message": "active/désactive le message de bienvenue en message privé",
            f"{prefix}clear <nbr/texte>": "supprime le nombres de messages,\nsupprime les messages jusqu'au lien donné",
            f"{prefix}nuke <salon>": "réinitialise le salon",
            f"{prefix}say <salon> <message>": "envoie un message dans un salon",
            f"{prefix}reaction <salon> <id du msg> <reactions>": "le bot réagit au message avec les réactions données, les réactions doivent être collées"
        },

        "🎮": {
            f"{prefix}10fastfinger": "écrirez des phrases le plus vite possible",
            f"{prefix}calcul_mental": "Donnez le résultat des calculs le plus vite possible",
            f"{prefix}puissance4 <id du membre/mention>": "jouez au puissance 4",
            f"{prefix}monopoly": "jouez au monopoly",
        },

        "🔧": {
            f"{prefix}random <nombre>": "donne un nombre aléatoire entre 0 et le nombre donné",
            f"{prefix}piece": "pile ou face",
            f"{prefix}ping": "ping le bot",
        },

        "📝": {
            f"{prefix}8ball <message>": "Boule magique",
            f"{prefix}hentai <categorie> <#nbr d'images>": "envoie des images de hentai /!\ le salon doit etre en nsfw",
            f"{prefix}pp <id du membre/mention>": "donne la pp du membre",
            f"{prefix}reddit <subreddit> <#nbr d'images>": "donne les images du subreddit",
        },

        "💬": {
            f"{prefix}bite <id du membre/mention>": "miaam",
            f"{prefix}baka <id du membre/mention>": "ba..baka !",
            f"{prefix}hug <id du membre/mention>": "🤗",
            f"{prefix}pat <id du membre/mention>": "pat pat",
            f"{prefix}kiss <id du membre/mention>": "😘",
            f"{prefix}bonjour <id du membre/mention>": "bonjour !"
        }
    }

    choix = "🏠"

    embed = discord.Embed(color=0xf0a3ff)
    embed.set_author(name=f"help - Eula, serveurs: {len(dico)}, version: {version_bot}",
                     icon_url=client.user.avatar_url)
    embed.add_field(name="contact", value="Si vous avez des retours a faire venez DM **kojhyy#0012**\n󠀮 ",
                    inline=False)

    for key, value in dico_help[choix].items():
        embed.add_field(name=key, value=value, inline=False)

    msg = await ctx.send(embed=embed)

    for emoji in liste_emoji:
        await msg.add_reaction(emoji)

    while True:
        reaction, _ = await client.wait_for("reaction_add", check=lambda r,
                                                                         u: u.id != client.user.id and r.message.id == msg.id and r.emoji in liste_emoji,
                                            timeout=60.0)
        choix = reaction.emoji
        await msg.remove_reaction(reaction.emoji, ctx.author)

        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"help - Eula, serveurs: {len(dico)}, version: {version_bot}",
                         icon_url=client.user.avatar_url)
        embed.add_field(name="contact", value="Si vous avez des retours a faire venez DM **kojhyy#0012**\n󠀮 ",
                        inline=False)

        for key, value in dico_help[choix].items():
            embed.add_field(name=key, value=value, inline=False)

        await msg.edit(embed=embed)


# - jeux
@client.command(aliases=["10fastfinger", "10ff"])
async def jeu_reaction(ctx, limit=5):
    list_user, dico_points = await start_game_multi(ctx, limit, "10fastfinger")
    if not list_user:
        return

    turn = 0

    def get_sentences():
        a = requests.get("https://enneagon.org/phrases").text

        a = a[a.find('<div class="main">') + 23: a.find("</div>") - 6]
        a = replaces(a, "&nbsp", "", ";", "", " <br>", "")
        for e in a:
            e = e.replace("É", "E")

        return [i.strip() for e in a.split(".") for i in e.split(",") if 70 > len(i) > 20]

    list_question = get_sentences()
    while turn != limit:

        mot = list_question[random.randint(0, len(list_question) - 1)]
        embed = discord.Embed(color=0xf0a3ff)
        embed.add_field(name="Phrase", value=mot, inline=False)
        await ctx.send(embed=embed)
        list_question.remove(mot)

        if len(list_question) == 0:
            list_question = get_sentences()
        try:
            msg = await client.wait_for("message",
                                        check=lambda message: message.author in list_user and message.content in [mot,
                                                                                                                  "exit",
                                                                                                                  "!exit",
                                                                                                                  "leave",
                                                                                                                  "!leave",
                                                                                                                  "Exit",
                                                                                                                  "!Exit",
                                                                                                                  "leave",
                                                                                                                  "Leave"],
                                        timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("partie finie à cause d'inactivité")
            break
        if msg.content.lower() in ["exit", "!exit", "leave", "!leave"]:
            await ctx.send("partie annulée !")
            return
        dico_points[msg.author.id] += 1
        await ctx.send(f"**{msg.author}** gagne le point ! {dico_points[msg.author.id]} points")
        turn += 1
        await asyncio.sleep(3)

    await end_game(ctx, list_user, dico_points)


@client.command()
async def calcul_mental(ctx, limit=5):
    list_user, dico_points = await start_game_multi(ctx, limit, "calcul mental")
    if not list_user:
        return

    turn = 0
    operateur = [1, 2]
    while turn != limit:
        ope = operateur[random.randint(0, len(operateur) - 1)]
        if ope == 1:
            calcul = f"{random.randint(0, 11)} * {random.randint(0, 11)}"
        elif ope == 2:
            nbr = random.randint(1, 2)
            list_ope = ["+", "-"]
            calcul = ""
            for i in range(nbr):
                calcul += " " + list_ope[random.randint(0, 1)] + " "
                calcul += f"{random.randint(-500, 500)} {list_ope[random.randint(0, 1)]} {random.randint(-500, 500)}"
            calcul = calcul[3:]

        embed = discord.Embed(color=0xf0a3ff)
        embed.add_field(name="Calcul", value=calcul, inline=False)
        await ctx.send(embed=embed)
        try:
            msg = await client.wait_for("message", check=lambda
                message: message.author in list_user and message.content.lower() in [str(eval(calcul)), "exit", "!exit",
                                                                                     "leave", "!leave"], timeout=180)
        except asyncio.TimeoutError:
            await ctx.send("partie finie à cause d'inactivité")
            break
        if msg.content.lower() in ["exit", "!exit", "leave", "!leave"]:
            await ctx.send("partie annulée !")
            return
        dico_points[msg.author.id] += 1
        await ctx.send(f"**{msg.author}** gagne le point ! {dico_points[msg.author.id]} points")
        turn += 1
        await asyncio.sleep(3)

    await end_game(ctx, list_user, dico_points)


@client.command()
async def monopoly(ctx, private=None):
    msg = await ctx.send("**Partie de Monopoly lancée !**\npour participer réagissez avec 🖐️")
    await msg.add_reaction("🖐️")
    await asyncio.sleep(12)
    list_user = []
    async for e in ctx.channel.history(limit=100):
        if e.id == msg.id:
            for reaction in e.reactions:
                if reaction.emoji == "🖐️":
                    async for user in reaction.users():
                        if user.id != client.user.id:
                            list_user.append(user)
            break

    if not list_user:
        await ctx.reply("Aucun joueur n'a rejoint la partie", mention_author=False)
        return

    elif len(list_user) == 1:
        await ctx.reply("Vous ne pouvez pas jouer seul")

    # --- déclaration des classes

    class Player:
        def __init__(self, discord, emote) -> None:
            # en lui meme
            self.discord = discord
            self.money = 2000
            self.lost = False

            # ses possessions
            self.properties = []
            self.train_station = 0
            self.card_jail = False

            # utile au programme
            self.emote = emote
            self.position = 0
            self.last_position = (12, 11)
            self.turn_jail = 0
            self.turn_protection = 0

        def jail(self):
            # le joueur vas en prison
            self.turn_jail = 2
            self.position = 10

        def move(self, number):
            # se déplace
            tmp = self.position
            self.position = self.position + number - 40 if self.position + number >= 40 else self.position + number
            if self.position < tmp:
                self.money += 200

        def buy(self, property):
            # achète une propriété
            self.money -= property.rent
            self.properties.append(property)

            if property.emote == "🚉":
                user.train_station += 1

            property.is_bought(self)
            board.property_is_bought(property)

        def lost_property(self, property):
            # perd une propriété
            self.properties.remove(property)

            board.property_is_sell(property)
            property.owner = None

        def mortgage(self, property):
            # hypothèque une propriété
            self.lost_property(property)
            self.money += int(property.rent / 2)

            board.property_is_sell(property)

        def game_over(self):
            # perd la partie
            self.lost = True
            list_player.remove(self)

            for property in self.properties.copy():
                self.lost_property(property)

            remove_emote(user.last_position, self)

    class Property:
        def __init__(self, name, rent, emote) -> None:
            self.name = name
            self.rent = rent
            self.emote = emote

            self.owner = None
            self.x_rent = 1.0

            self.benefit = 0

        def is_bought(self, player):
            self.owner = player
            self.x_rent = 1.0

        def get_rent(self) -> int:
            station_bonus = 100 * self.owner.train_station - 1 if self.emote == "🚉" else 0
            return int(self.rent * self.x_rent + station_bonus)

        def increase_x_rent(self):
            self.x_rent += 0.05

    class _board:
        def __init__(self, list_square) -> None:
            self.properties_left = [case for case in list_square if isinstance(case, Property)]
            self.all_properties = self.properties_left.copy()
            self.player_same_square = {}

        def property_is_bought(self, property):
            self.properties_left.remove(property)

        def property_is_sell(self, property):
            self.properties_left.append(property)

    # -- déclaration des fonctions

    def luck():
        nbr = random.randint(min, max)
        if nbr == -1:
            user.money += 200
            return "tony à arrêté d'être gay, tu perds moins d'argent en capote, gagne 200 ₿"
        elif nbr == 0:
            user.money += 200
            return "tony a arrêté d'être gay, tu perds moins d'argent en capote, gagne 200 ₿"
        elif nbr == 1:
            user.position = 0
            user.money += 100
            return "Retournez a la case départ et touchez 100 ₿"
        elif nbr == 2:
            msg = "Un furry vous pourchasse vous allez au parc gratuit"
            if user.position >= 21:
                user.money += 200
                msg += "\nvous passez par la case départ et recevez 100 ₿"
            user.position = 20
            return msg
        elif nbr == 3:
            user.money -= 125
            return "Vous avez gagné un iphone 13 !\nmais c'était une arnaque -300 ₿"
        elif nbr == 4:
            user.position = random.randint(0, 40)
            return "Blitzcrank vous a attrapé, il vous téléporte aléatoirement sur le plateau"
        elif nbr == 5:
            for player_ in list_player:
                user.money += 75
                player_.money -= 75
            return "C'est ton anniv Bro!!! les autres joueurs doivent te donner 75 ₿ or Konsékens"
        elif nbr == 6:
            user.money += 325
            return "SIUUUUUU ! Oh mon dieu Ronaldo viens vous voir et vous donne 325 ₿"
        elif nbr == 7:
            user.money = int(user.money * 0.95)
            return "Les gros rats de la banque vous vole 5% de votre richesse"
        elif nbr == 8:
            user.money += 175
            return "Tu es très beau donc tu gagne un concours de beauté >u<. + 175 ₿"
        elif nbr == 9:
            user.money -= 100
            return "Tu as perdu une battle de rap contre JUL... le monde te desteste maintenant et ta famille te renies... -100 ₿"
        elif nbr == 10:
            user.money -= 200
            return "OMG banner de Klee ! perd 200 ₿. sad ta pity sur Qiqi"
        elif nbr == 11:
            user.money -= 160
            return "Tu as perdu ton porte feuille... 160 Balles en moins. T'es trop con aussi bro"
        elif nbr == 12:
            user.money += 225
            return "Tu vends tes pieds sur Onlyfans + 225 ₿"
        elif nbr == 13:
            user.money -= 175
            return "Tu as trop rager sur Clash royal tu as cassé ton téléphone, il faut te le repayer, - 175 ₿"
        elif nbr == 14:
            user.money -= 250
            return "Tu as rencontrer une e-girl HYPER BONNE!!! ton coeur est comblé mais tu as plus d'argent de poche... -250 ₿"
        elif nbr == 15:
            user.money += 400
            return "tu as gagné au loto, o_0 + 400 ₿"
        elif nbr == 16:
            user.money += 300
            user.jail()
            return "Tu écris le meilleur hentai de loli, gagne 300 ₿ mais perds ta santée mentale et va en prison"
        elif nbr == 17:
            user.money += 125
            return "Tu touches l'héritage de tonton jean-ma, gagne 125 ₿"
        elif nbr == 18:
            user.money += 100
            return "Tu as gagner au loto mais ton père a enfin fini d'acheter des clopes donc au lieu de gagner 1000 ₿ tu gagne 100 ₿"
        elif nbr == 19:
            property_ = list_square[21]
            msg = "Tu deviens premier ministre des randoms, acquière l'avenue matignon"
            if property_.owner is None:
                user.buy(property_)
                user.money += property_.rent
            elif property_.owner == user:
                msg += "\nmais tu possède deja cette avenue !"
            else:
                msg += f", si déjà occupée,\nle propriétaire te doit le prix d'acquisition donc **{property_.owner.discord.name}** paye {property_.rent} ₿"
                if property_.owner.money - property_.rent < 0:
                    msg += f"{property_.owner} n'a pas assez d'argent pour payer ! il est donc éliminer"
                    property_.owner.game_over()
                else:
                    property_.owner.money -= property_.rent
                    user.money += property_.rent
            return msg
        elif nbr == 20:
            user.money -= 250
            return "tu es mort. tu doit payer 250 ₿ pour pouvoir t'enterrer"
        elif nbr == 21:
            user.money -= 100
            return "la littérature française t'a aider a avancer ! +10 point en intelligence mais -100€ pour tous les livres acheté"
        elif nbr == 22:
            random_user = random.choice(list_player)
            text = f"**{random_user.discord.name}** intente un procès contre vous ! le gagnant gagne 200 ₿\nle resultat se joue sur un pile(vous gagnez) ou face(vous perdez)\n"
            if random.randint(0, 1):
                tmp = 200
                text += f"\n*le juge lance la piece ...*\nFACE\n **{random_user.discord.name}** gagné"
            else:
                tmp = -200
                text += f"\n*le juge lance la piece ...*\nPILE\n **{user.discord.name}** gagné"
            user.money -= tmp
            random_user.money -= -tmp
            return text
        elif nbr == 23:
            user.money -= 238
            return "la congolexicomatisation des lois du marché congolais a augmenter ta thune +238 ₿"
        elif nbr == 24:
            user.money += 12
            return "Eric Zemmour est passé au pouvoir et t'as dégagé de la france mais avec de l'argent pour que tu puissent a minima vivre. -1 pays mais +12€"
        elif nbr == 25:
            user.turn_protection += 1
            return "Tu migre a malte, tu ne paye pas au prochain tour"
        elif nbr == 26:
            user.turn_protection += 2
            return "Tu as un compte en banque en Suisse!!! tu est immunisé a toute facture (maison/taxe) pendant 2 tours."
        elif nbr == 27:
            user.card_jail = True
            return "Un mafieux peut corrompre la garde de la prison pour toi\ncette carte peux être utilisé plus tard"
        elif nbr == 28:
            return "Tu as voler de la nourriture a un Africain. +100 de riz et c'est tout TA CRU KOI TOUA"
        elif nbr == 29:
            for player_ in list_player:
                player_.position = 0
            return "tout le monde retourne a la case départ !"
        elif nbr == 30:
            for player_ in list_player:
                player_.money -= 100
            user.money += 100 * len(list_player) - 1
            return "tu crée un commerce de ton eau de bain de femboy, chaque joueurs en achète pour 100 ₿"
        elif nbr == 31:
            for player_ in list_player:
                player_.money -= 50
            user.money += 50 * len(list_player) - 1
            user.money += 200
            return "Tu as empeché Hitler de se suicider, +200 ₿ et +50 ₿ des joueurs pour cet exploit monumentale"
        elif nbr == 32:
            user.money -= 650
            return "Tu vote Sandrine Rousseau ?\nRATIO -650 ₿"

    def print_board():
        # transforme la matrice en texte qui sera affiché sur discord
        msg = ""
        for list_of_emote in matrice_board:
            for emote in list_of_emote:
                msg += emote
            msg += "\n"
        return msg

    def place_emote(tupl, user):
        # place l'emoji du joueur sur la matrice
        pos = matrice_board[tupl[0]][tupl[1]]
        if pos in list_emote:

            for user_bis in list_player:
                if user_bis.emote == pos:
                    board.player_same_square[tupl] = [user_bis, user]
                    matrice_board[tupl[0]][tupl[1]] = "2️⃣"

        elif tupl in board.player_same_square:
            board.player_same_square[tupl] = board.player_same_square[tupl] + [user]
            dico = {
                2: "2️⃣",
                3: "3️⃣",
                4: "4️⃣",
                5: "5️⃣",
                6: "6️⃣",
                7: "7️⃣",
                8: "8️⃣",
                9: "9️⃣"
            }

            matrice_board[tupl[0]][tupl[1]] = dico[len(board.player_same_square[tupl])]
        else:
            matrice_board[tupl[0]][tupl[1]] = user.emote

    def remove_emote(tupl, user):
        # enleve l'emoji du joueur de la matrice

        if tupl in board.player_same_square:

            if len(board.player_same_square[tupl]) == 2:
                board.player_same_square[tupl].remove(user)
                matrice_board[tupl[0]][tupl[1]] = board.player_same_square[tupl][0].emote
                board.player_same_square.pop(tupl)

            else:
                board.player_same_square[tupl].remove(user)
                dico = {
                    2: "2️⃣",
                    3: "3️⃣",
                    4: "4️⃣",
                    5: "5️⃣",
                    6: "6️⃣",
                    7: "7️⃣",
                    8: "8️⃣",
                    9: "9️⃣"
                }

                matrice_board[tupl[0]][tupl[1]] = dico[len(board.player_same_square[tupl])]
        else:
            matrice_board[tupl[0]][tupl[1]] = "⬛"

    def place_player(user):
        # actualise la position de tout les joueurs
        pos = user.position
        remove_emote(user.last_position, user)

        if 0 <= pos <= 10:
            pos_ = (12, 11 - pos)
        elif 11 <= pos <= 20:
            pos -= 10
            pos_ = (11 - pos, 0)
        elif 21 <= pos <= 30:
            pos -= 20
            pos_ = (0, 1 + pos)
        else:
            pos -= 31
            pos_ = (2 + pos, 12)

        place_emote(pos_, user)
        user.last_position = pos_

    def random_emote():
        # donne une emote aléatoire
        tmp = random.choice(prepa_emote)
        prepa_emote.remove(tmp)
        list_emote.append(tmp)
        return tmp

    async def put_emotes(list_of_emotes):
        # met les emotes sur le msg
        try:
            for emote in list_of_emotes:
                await msg.add_reaction(emote)
        except:
            await msg.clear_reactions()
            for emote in list_emote_game + list_of_emotes:
                await msg.add_reaction(emote)

    def hearder_msg():
        return f"{user.discord.mention}, ₿: {user.money}, 🏠: {len(user.properties)}"

    async def ask(dice_, action):
        await msg.edit(embed=discord_embed(hearder_msg(), dice_, action))
        await put_emotes(["✅", "❌"])

        try:
            emoji, user_ = await client.wait_for("reaction_add",
                                                 check=lambda reaction, user_: user_.id == user.discord.id and str(
                                                     reaction.emoji) in ["✅", "❌"] and reaction.message.id == msg.id,
                                                 timeout=300)
        except asyncio.TimeoutError:
            pass

        await msg.remove_reaction(emoji, user_)

        return emoji, user_

    def discord_embed(username, dice, action):
        # créer un embed discord
        embed = discord.Embed()
        embed.add_field(name="Plateau, cases restantes: " + str(len(board.properties_left)), value=print_board(),
                        inline=True)
        embed.add_field(name="Tour de", value=username, inline=False)
        embed.add_field(name="dé", value=dice, inline=False)
        embed.add_field(name="action", value=action, inline=False)
        return embed

    async def wait_reactions():
        # fonction main, attends une reaction

        await msg.edit(embed=discord_embed(hearder_msg(), "en attente...", "..."))

        # si le joueur est en prison et a une carte pour sortir de prison
        if user.turn_jail != 0 and user.card_jail:
            emoji, _ = await ask("...", f"**{user.discord.name}**, voulez-vous utilisez votre carte sortie de prison ?")

            if str(emoji.emoji) == "✅":
                user.turn_jail = 0
                user.card_jail = False
                text = "Vous avez utilisez votre carte !"
            else:
                text = "Vous n'avez pas utilisez votre carte !"
            await msg.edit(embed=discord_embed(hearder_msg(), f"...", text))

            await asyncio.sleep(3)

        # si le joueur n'est pas en prison
        if user.turn_jail == 0:
            # attends que le joueur utilise une reaction
            try:
                emoji, _ = await client.wait_for("reaction_add",
                                                 check=lambda reaction, user_: user_.id == user.discord.id and str(
                                                     reaction.emoji) in list_emote_game + ["🛑", "🔄"], timeout=300)
            except asyncio.TimeoutError:
                # si le joueur est afk on passe son tour
                await msg.edit(
                    embed=discord_embed(hearder_msg(), "...", f"{user.discord.name} n'a pas joué on saute son tour"))
                await asyncio.sleep(3)
                return False

            await msg.remove_reaction(emoji, user.discord)

            if str(emoji.emoji) == "🎲":
                await play()

            elif str(emoji.emoji) == "ℹ️":

                msgs = []
                tmp = 0
                embed = discord.Embed(title="emote: nom, loyer, proprietaire, benefice")
                for emote in ["🚉", "🟫", "🟦", "🟪", "🟧", "🟥", "🟨", "🟩", "⬜"]:
                    text = ""
                    for property_ in [property_ for property_ in board.all_properties if property_.emote == emote]:
                        text += f"{property_.emote}: {property_.name}, {property_.rent if property_.owner is None else property_.get_rent()}, {'aucun' if property_.owner is None else property_.owner.discord.name}, {property_.benefit}\n"
                    embed.add_field(name="case:", value=text, inline=False)
                    tmp += 1
                    if tmp == 5 or tmp == 9:
                        msgs.append(await ctx.send(embed=embed))
                        embed = discord.Embed()

                await put_emotes("❌")

                try:
                    num, _ = await client.wait_for("reaction_add",
                                                   check=lambda reaction, user_: user_.id == user.discord.id and str(
                                                       reaction.emoji) == "❌" and msg.id == reaction.message.id,
                                                   timeout=300)
                except asyncio.TimeoutError:
                    pass

                await msg.clear_reaction("❌")

                for msg_ in msgs:
                    await msg_.delete()
                await wait_reactions()

            elif str(emoji.emoji) == "🛑":
                await msg.edit(embed=discord_embed("...", "...", "partie annulée"))
                return True

            elif str(emoji.emoji) == "🏳️":
                emoji, _ = await ask("...", f"**{user.discord.name}** voulez-vous vraiment abandonner ?")

                if str(emoji.emoji) == "✅":
                    for react in ["❌", "✅"]:
                        await msg.clear_reaction(react)
                    await msg.edit(embed=discord_embed(hearder_msg(), "...", "vous avez abandonné !"))
                    user.game_over()
                else:
                    for react in ["❌", "✅"]:
                        await msg.clear_reaction(react)
                    await wait_reactions()

            elif str(emoji.emoji) == "⬆️":
                if len(user.properties) == 0:
                    await msg.edit(embed=discord_embed(hearder_msg(), "...", "Vous possedez aucune propriété !"))
                price_upgrade = 75 * len(user.properties)
                num, _ = await ask("...",
                                   f"**{user.discord.name}** voulez-vous payer {price_upgrade} ₿\n pour augmenter le loyer de toutes vos propriétés de 5 % ?")

                if str(num.emoji) == "✅":
                    user.money -= price_upgrade

                    for property_ in user.properties:
                        property_.increase_x_rent()

                    text = "Le loyer de toutes vos propriétés a été augmenté !"
                else:
                    text = "opération annulée"
                await msg.edit(embed=discord_embed(hearder_msg(), "...", text))

                for react in ["❌", "✅"]:
                    await msg.clear_reaction(react)

                await asyncio.sleep(3)
                await wait_reactions()

            elif str(emoji.emoji) == "🏦":
                text = "".join(f"{property_.emote}: {property_.name}, {int(property_.rent / 2)}\n" for property_ in
                               user.properties)
                if text == "":
                    await msg.edit(embed=discord_embed(hearder_msg(), "...", "Vous possedez aucune propriété !"))
                    await asyncio.sleep(4)
                    await wait_reactions()
                    return False

                embed = discord.Embed()
                embed.add_field(name=f"Argent", value=f"{user.money} ₿", inline=False)
                embed.add_field(name="Instructions",
                                value=f"**{user.discord.name}** écrivez le nom des propriétés a vendre et \"leave\" pour quitter",
                                inline=False)
                embed.add_field(name="prix de vente", value=text, inline=False)
                msg_info = await ctx.send(embed=embed)

                name_properties = [property_.name.lower() for property_ in user.properties]

                content = ""

                while True:
                    try:
                        message = await client.wait_for("message", check=lambda
                            message: message.author.id == user.discord.id and message.channel.id == msg.channel.id,
                                                        timeout=300)
                    except asyncio.TimeoutError:
                        await msg_info.delete()
                        await wait_reactions()
                        return False

                    content = message.content.lower()

                    text = "".join(f"{property_.emote}: {property_.name}, {int(property_.rent / 2)}\n" for property_ in
                                   user.properties)
                    if content in ["leave", "quit", "quitter", "partir"] or text == "":
                        await message.delete()
                        await msg_info.delete()
                        await wait_reactions()
                        return False

                    else:
                        embed = discord.Embed()
                        embed.add_field(name=f"Argent", value=f"{user.money} ₿", inline=False)
                        embed.add_field(name="Instructions",
                                        value=f"**{user.discord.name}** écrivez le nom des propriétés a vendre et leave pour arreter",
                                        inline=False)
                        embed.add_field(name="prix de vente", value=text, inline=False)

                        if content in name_properties:
                            index = name_properties.index(content)
                            user.mortgage(user.properties[index])
                            embed.add_field(name="info", value=f"\"{content}\" a bien été vendu", inline=False)

                        else:
                            embed.add_field(name="info",
                                            value=f"\"{content}\" n'est pas une propriété ou elle ne vous appartient pas\"",
                                            inline=False)
                        await msg_info.edit(embed=embed)
                        await asyncio.sleep(3)
                        await message.delete()

            elif str(emoji.emoji) == "🔄":
                await put_emotes(list_emote_game)
                await wait_reactions()

            return False

    async def play():
        # le joueur lance les dés
        await msg.edit(embed=discord_embed(hearder_msg(), "lancement du dé...", "..."))
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        replay = False

        dice = dice1 + dice2
        if dice1 == dice2:
            dice = str(dice) + ", double "
            replay = True

        # déplace le joueur
        user.move(dice1 + dice2)
        place_player(user)
        square = list_square[user.position]

        # propriété
        if isinstance(square, Property):

            # si le joueur est chez lui
            if square.owner == user:
                square.increase_x_rent()
                str_ = str(square.x_rent)[2:4]
                str_nbr = str_ + "0" if len(str_) == 1 else str_
                text = f"**{user.discord.name}** vous êtes chez vous !\nle loyer augmente de {str_nbr} %, ( {square.get_rent()} ₿ )"

            elif square.rent < user.money and square.owner is None:
                emoji, _ = await ask(f"le dé est tombé sur ... {dice} !",
                                     f"**{user.discord.name}** voulez-vous acheter {square.name} pour {square.rent} ₿ ?")

                if str(emoji.emoji) == "✅":
                    user.buy(square)
                    text = f"**{user.discord.name}** vous avez acheté {square.name} !"
                else:
                    text = f"**{user.discord.name}** vous n'avez pas acheté {square.name} !"

            else:
                if user.turn_protection != 0:
                    text = f"vous devez payer {square.rent if square.owner is None else square.get_rent()} ₿\nmais vous êtes sous protection de carte chance"

                elif square.rent > user.money and square.owner is None:
                    text = f"**{user.discord.name}** vous n'avez pas assez d'argent pour acheter {square.name}"

                elif square.get_rent() < user.money and square.owner is not None:
                    user.money -= square.get_rent()
                    square.owner.money += square.get_rent()
                    square.benefit += square.get_rent()
                    text = f"**{user.discord.name}** paye {square.get_rent()} ₿ a **{square.owner.discord.name}** !"

                elif square.get_rent() > user.money and square.owner is not None:
                    text = f"**{user.discord.name}** vous n'avez pas assez d'argent pour payer le loyer ! il est donc éliminer\n**{square.owner.discord.name}** gagne que {user.money} ₿"
                    user.game_over()
                    square.owner.money += user.money
                    square.benefit += user.money
                    await asyncio.sleep(3)

        # case chance
        elif callable(square):
            text = luck()
            for player_ in list_player:
                place_player(player_)
            await asyncio.sleep(2)
            await msg.edit(embed=discord_embed(hearder_msg(), f"le dé est tombé sur ... {dice} !", text))
            await asyncio.sleep(2)

        # case impots
        elif len(square) == 2:
            if square[1] < user.money:
                user.money -= square[1]
                text = f"**{user.discord.name}** vous devez payer les {square[0]}, {square[1]} ₿"

            elif square[1] > user.money:
                user.game_over()
                text = f"**{user.discord.name}** vous devez payer les {square[0]}, {square[1]} ₿\nmais vous n'avez pas assez d'argent, vous êtes donc éliminer !"

        # case spécial
        elif type(square) is str:
            if square == "départ":
                text = "vous recevez 200 ₿ !"
                user.money += 100

            elif square == "prison":
                text = "vous visitez la prison, bizarrement il y a que des noirs et des arabes"

            elif square == "parc gratuit":
                text = "vous visitez le parc gratuit"

            else:
                text = "le policier vous a pris pour un noir ! il vous jete en prison"
                user.jail()

        await msg.edit(embed=discord_embed(hearder_msg(), f"le dé est tombé sur ... {dice} !", text))

        for react in ["❌", "✅"]:
            await msg.clear_reaction(react)

        if replay and not user.lost:
            await asyncio.sleep(4)
            await wait_reactions()

    # -- déclaration des variables

    list_square = []
    for values in [["départ"], ["boulevard de belleville", 60, "🟫"], [luck], ["rue lecoubre", 60, "🟫"],
                   ["impôts sur le revenue", 200], ["gare monparnasse", 200, "🚉"], ["rue de vaugirard", 100, "🟦"],
                   [luck], ["rue de courcelles", 100, "🟦"], ["avenue de la republique", 120, "🟦"], ["prison"],
                   ["boulevard de la vilette", 140, "🟪"], [luck], ["avenue de neuilly", 140, "🟪"],
                   ["rue de paradis", 160, "🟪"], ["gare de Lyon", 200, "🚉"], ["avenue mozart", 180, "🟧"], [luck],
                   ["boulevard saint-michel", 180, "🟧"], ["place pigalle", 200, "🟧"], ["parc gratuit"],
                   ["avenue matignon", 220, "🟥"], [luck], ["boulevard malesherbes", 220, "🟥"],
                   ["avenue henri-martin", 240, "🟥"], ["gare du nord", 200, "🚉"],
                   ["faurbourg saint-honoré", 260, "🟨"], ["place de la bourse", 260, "🟨"], [luck],
                   ["rue la fayette", 280, "🟨"], ["allez en prison"], ["avenue de breteuil", 300, "🟩"],
                   ["avenue foch", 300, "🟩"], [luck], ["boulevard des capucines", 320, "🟩"],
                   ["gare de saint-Lazare", 200, "🚉"], [luck], ["avenue des champs-élysées", 350, "⬜"],
                   ["taxes de luxe", 100], ["rue de la paix", 400, "⬜"]]:
        if len(values) == 3:
            list_square.append(Property(values[0], values[1], values[2]))
        elif len(values) == 2:
            list_square.append([values[0], values[1]])
        elif len(values) == 1 and type(values[0]) is str:
            list_square.append(values[0])
        else:
            list_square.append(values[0])

    board = _board(list_square)

    matrice_board = [
        ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        ["⬛", "🚗", "🟥", "❔", "🟥", "🟥", "🚉", "🟨", "🟨", "❔", "🟨", "👮", "⬛"],
        ["⬛", "🟧", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "🟩", "⬛"],
        ["⬛", "🟧", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "🟩", "⬛"],
        ["⬛", "❔", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "❔", "⬛"],
        ["⬛", "🟧", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "🟩", "⬛"],
        ["⬛", "🚉", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "🚉", "⬛"],
        ["⬛", "🟪", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "❔", "⬛"],
        ["⬛", "🟪", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬜", "⬛"],
        ["⬛", "❔", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "💵", "⬛"],
        ["⬛", "🟪", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬜", "⬛"],
        ["⬛", "⛓️", "🟦", "🟦", "❔", "🟦", "🚉", "💵", "🟫", "❔", "🟫", "⬅️", "⬛"],
        ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"]
    ]

    min = 1 if private == "normal" else -1
    max = 32

    prepa_emote = ["💤", "🦑", "🦥", "♿", "🛒", "👑", "☃️", "🐷", "🐭", "🐐", "🍩", "🎏", "☄️", "🦦", "🍑", "🛺", "🦉",
                   "🦀"]
    list_emote = []
    list_emote_game = ["🎲", "ℹ️", "⬆️", "🏳️", "🏦"]

    list_player = [Player(_user, random_emote()) for _user in list_user]
    random.shuffle(list_player)

    embed = discord.Embed()
    for player_ in list_player:
        embed.add_field(name=player_.discord.name, value=player_.emote, inline=True)
    await ctx.send(embed=embed)

    msg = await ctx.send(embed=discord_embed("...", "...", "..."))
    await put_emotes(list_emote_game)

    index_player = 0

    while True:
        user = list_player[index_player]

        if len(list_player) == 1:
            await msg.edit(embed=discord_embed("...", "...", f"Partie terminée le gagnant est {user.discord.mention}"))
            return

        if await wait_reactions():
            return

        if user.turn_protection != 0:
            user.turn_protection -= 1

        await asyncio.sleep(4)
        index_player = 0 if index_player >= len(list_player) - 1 else index_player + 1


@client.command(aliases=["p4"])
async def puissance4(ctx, member):
    response, member = await start_game_duo(ctx, member, "puissance 4")
    if response is False:
        return

    rond_gris = "⚫"
    rond_rouge = "🔴"
    rond_jaune = "🟡"

    if bool(random.getrandbits(1)):
        dico_p4 = {"rouge": (ctx.author, rond_rouge, 0xdd2e44), "jaune": (member, rond_jaune, 0xfdcB58)}
    else:
        dico_p4 = {"jaune": (ctx.author, rond_jaune, 0xfdcB58), "rouge": (member, rond_rouge, 0xdd2e44)}

    plateau = [[rond_gris for _ in range(7)] for _ in range(6)]

    def str_plateau(matrice):
        msg = ""
        for i in matrice:
            for j in i:
                msg += j
            msg += "\n"
        return msg

    couleur = "jaune"

    async def send():
        embed = discord.Embed(color=0x000000, title="Puissance 4")
        embed.add_field(name="Preparation", value="...", inline=False)
        embed.add_field(name="Plateau", value=f"1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n{str_plateau(plateau)}", inline=False)
        msg = await ctx.send(embed=embed)
        for e in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "🔄", "⬇️"]:
            await msg.add_reaction(e)
        return msg

    msg = await send()

    async def edit_embed(title=None, message=None):
        embed = discord.Embed(color=dico_p4[couleur][2], title="Puissance 4")
        embed.add_field(name="Tour de", value=dico_p4[couleur][0].mention, inline=False if title is None else True)
        if title is not None:
            embed.add_field(name=title, value=message, inline=True)
        embed.add_field(name="Plateau", value=f"1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n{str_plateau(plateau)}", inline=False)
        await msg.edit(embed=embed)

    async def end():
        try:
            num, user = await client.wait_for("reaction_add",
                                              check=lambda reaction, user: str(reaction.emoji) == "🔄" and user.id in [
                                                  dico_p4["rouge"][0].id, dico_p4["jaune"][0].id], timeout=30)
        except asyncio.TimeoutError:
            return None
        plateau = [[rond_gris for _ in range(7)] for _ in range(6)]
        await msg.remove_reaction(num.emoji, user)
        return plateau

    while True:
        while plateau[0].count(rond_gris) != 0:
            await edit_embed()

            try:
                num, _ = await client.wait_for("reaction_add",
                                               check=lambda reaction, user: str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣",
                                                                                                    "4️⃣", "5️⃣", "6️⃣",
                                                                                                    "7️⃣", "🔄",
                                                                                                    "⬇️"] and user.id ==
                                                                            dico_p4[couleur][0].id, timeout=180)
            except asyncio.TimeoutError:
                return
            await msg.remove_reaction(num.emoji, dico_p4[couleur][0])
            if str(num.emoji) == "⬇️":
                await msg.delete()
                msg = await send()
            elif str(num.emoji) == "🔄":
                plateau = [[rond_gris for _ in range(7)] for _ in range(6)]
            else:
                dict_number = {
                    "1️⃣": 0,
                    "2️⃣": 1,
                    "3️⃣": 2,
                    "4️⃣": 3,
                    "5️⃣": 4,
                    "6️⃣": 5,
                    "7️⃣": 6
                }

                def place():
                    for i in range(len(plateau)):
                        if plateau[len(plateau) - i - 1][dict_number[num.emoji]] == rond_gris:
                            plateau[len(plateau) - i - 1][dict_number[num.emoji]] = dico_p4[couleur][1]
                            return len(plateau) - i - 1, dict_number[num.emoji]
                    return -1, -1

                positionx, positiony = place()

                if (positionx, positiony) == (-1, -1):
                    await ctx.send(
                        f"{dico_p4[couleur][0].mention} la colonne {dict_number[num.emoji] + 1} est pleine !")
                else:

                    listex = plateau[positionx]
                    listey = [plateau[i][positiony] for i in range(6)]

                    listeDiago1 = [plateau[positionx - i][positiony - i] for i in range(0, 7) if
                                   positionx - i >= 0 and positiony - i >= 0]
                    listeDiago1.reverse()
                    listeDiago1 += [plateau[positionx + i][positiony + i] for i in range(1, 7) if
                                    positiony + i < 7 and positionx + i < 6]
                    listeDiago1.reverse()

                    listeDiago2 = [plateau[positionx - i][positiony + i] for i in range(0, 7) if
                                   positionx - i >= 0 and positiony + i <= 6]
                    listeDiago2.reverse()
                    listeDiago2 += [plateau[positionx + i][positiony - i] for i in range(1, 7) if
                                    positionx + i < 6 and positiony - i >= 0]
                    listeDiago2.reverse()

                    for liste in [listex, listey, listeDiago1, listeDiago2]:
                        tmp = "".join(liste)
                        if tmp.count(dico_p4[couleur][1]) != tmp.replace(dico_p4[couleur][1] * 4, "").count(
                                dico_p4[couleur][1]):
                            await edit_embed("Vainqueur", dico_p4[couleur][0].mention)
                            plateau = await end()

                    if couleur == "jaune":
                        couleur = "rouge"
                    else:
                        couleur = "jaune"

        await edit_embed("Egalité", "󠀮 ")
        plateau = await end()
        if plateau is None:
            return


@puissance4.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque le membre a affronter ! syntaxe: {prefix}puissance4 <id du membre/mention>")


# - admin
@client.command(aliases=["config", "dico"])
async def view_config(ctx, option=None):
    if ctx.author.id != 236853417681616906:
        return

    if option == "all":
        msg = dico
    else:
        msg = dico[ctx.message.guild.id]

    await ctx.send(msg)


@client.command()
@has_permissions(administrator=True)
async def reaction(ctx, channel, id, *, react):
    if not channel.isdigit():
        channel = replaces(channel, "<#", "", ">", "")

    channel = client.get_channel(int(channel))
    if channel is None:
        await ctx.send("channel non trouvé")
    else:
        msg = await channel.fetch_message(int(id))
        react = react.replace(" ", "")
        liste = []
        previous = 0
        for i in range(len(react) - 2):
            if react[i] + react[i + 1] == "><":
                liste.append(react[previous:i + 1])
                previous = i + 1

        liste.append(react[previous:])
        for e in liste:
            await msg.add_reaction(e)
        await ctx.message.add_reaction("✅")


@reaction.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("L'id correspond à auncun message ou le bot ne peux pas mettre la réaction saisie")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque des arguments ! syntaxe: {prefix}reaction <salon> <id du msg> <reactions>")


@client.command()
@has_permissions(administrator=True)
async def toggle_welcome_message(ctx, msg=None):
    if dico[ctx.guild.id]["welcome_msg"] is None:
        if msg is None:
            await ctx.send(
                f"**quel message de bienvenue voulez-vous mettre ?**\npour que le bot écrive le nom du nouvel arrivant dans message écrivez $username$\nexemple: le message \"bienvenue $username$\" donnera \"bienvenue {ctx.author.name}\"")
            response = await client.wait_for("message", check=lambda
                message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=180)
            msg = response.content
        dico[ctx.guild.id]["welcome_msg"] = msg
        dico_update()
        await ctx.send("le nouveau message de bienvenue est enregistré")
    else:
        await ctx.send(
            f"Le message actuel est \n\n\"{dico[ctx.guild.id]['welcome_msg']}\" \n\nVoulez-vous désactivé le message de bienvenue ?")
        response = await client.wait_for("message", check=lambda
            message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id and message.content.lower() in [
            "o", "oui", "yes", "y", "no", "n", "non"], timeout=180)
        if response.content.lower() in ["o", "oui", "yes", "y"]:
            dico[ctx.guild.id]["welcome_msg"] = None
            dico_update()
            await ctx.send("La fonction message de bienvenue est désactivée")
        else:
            await response.add_reaction("✅")


@client.command()
@has_permissions(administrator=True)
async def say(ctx, channel, *, message):
    if not channel.isdigit():
        channel = replaces(channel, "<#", "", ">", "")

    channel = client.get_channel(int(channel))
    if channel is None:
        await ctx.send("channel non trouvé")
    else:
        await channel.send(message)
        await ctx.message.add_reaction("✅")


@say.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque le salon ! syntaxe: {prefix}say <salon> <message>")


@client.command()
@has_permissions(administrator=True)
async def toggle_autorole(ctx, role: discord.Role = None):
    if dico[ctx.guild.id]["autorole"] is None:
        if role is None:
            await ctx.send("quel rôle voulez-vous mettre ?")
            response = await client.wait_for("message", check=lambda
                message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=30)
            if "<@&" not in response.content.lower():
                await ctx.send(f"\"{response.content}\" n'est pas un rôle")
                return
            id = replaces(response.content, "<@&", "", ">", "")
            role = discord.utils.get(ctx.author.guild.roles, id=int(id))
            await check_permissions(ctx)
        dico[ctx.guild.id]["autorole"] = role.id
        dico_update()
        await ctx.send(f"Le rôle **{role.name}** est maintenant donné à tous les nouveaux arrivant !")
    else:
        dico[ctx.guild.id]["autorole"] = None
        dico_update()
        await ctx.send("La fonction d'autorole est maintenant désactivée")


@client.command(aliases=["c"])
@has_permissions(administrator=True)
async def clear(ctx, *, arg="1"):
    if arg.isdigit():
        await ctx.channel.purge(limit=int(arg) + 1)
    else:
        tmp = 0
        async for message in ctx.history(limit=500):
            tmp += 1
            if message.jump_url == arg:
                await ctx.send(
                    f"{tmp - 2} messages sélectionnés jusqu'au message demandé. voulez-vous les supprimer ? (oui/non)")
                msg = await client.wait_for("message", check=lambda message: message.author == ctx.author)
                if msg.content.lower() in ["oui", "o", "y", "yes"]:
                    await ctx.channel.purge(limit=tmp + 1)
                else:
                    await msg.add_reaction("✅")
                return


@client.command()
@has_permissions(administrator=True)
async def nuke(ctx, channel=None):
    if channel is None:
        await ctx.send("quel salon voulez-vous supprimer ?")
        channel = await client.wait_for("message", check=lambda
            message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=30)

    if not channel.isdigit():
        channel = replaces(channel, "<#", "", ">", "")

    channel = client.get_channel(int(channel))
    if channel not in ctx.channels:
        await ctx.send("salon non trouvé")
        return

    await ctx.send(f"Voulez-vous vraiment remettre à zéro le salon {channel.mention} ?")
    try:
        reponse = await client.wait_for("message", check=lambda
            message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("délai dépassé")
        return
    if reponse.content.lower() in ["yes", "y", "o", "oui"]:
        await ctx.guild.create_text_channel(channel.name, overwrites=channel.overwrites, category=channel.category,
                                            position=channel.position, topic=channel.topic, nsfw=channel.nsfw,
                                            slowmode_delay=channel.slowmode_delay)
        await channel.delete()
        await ctx.send(f"Le salon **{channel.name}** à été nuke !")


@client.command()
@has_permissions(administrator=True)
async def toggle_rolevocal(ctx, role: discord.Role = None):
    if dico[ctx.guild.id]["voc"] is None:
        if role is None:
            await ctx.send("quel rôle voulez-vous mettre ?")
            response = await client.wait_for("message", check=lambda
                message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=30)
            if "<@&" not in response.content.lower():
                await ctx.send(f"\"{response.content}\" n'est pas un rôle")
                return
            id = replaces(response.content, "<@&", "", ">", "")
            role = discord.utils.get(ctx.author.guild.roles, id=int(id))
            await check_permissions(ctx)
        dico[ctx.guild.id]["voc"] = role.id
        dico_update()
        await ctx.send(
            f"Le rôle **{role.name}** est maintenant donné à toutes les personnes qui rentre dans un salon vocal !")
    else:
        dico[ctx.author.guild.id]["voc"] = None
        dico_update()
        await ctx.send("Plus aucun rôle ne sera donné quand quelqu'un rejoint un salon vocal")


@client.command()
@has_permissions(administrator=True)
async def toggle_logs(ctx):
    if dico[ctx.author.guild.id]["logs"] is None:
        await ctx.send("Dans quel salon voulez-vous activer les logs ?")
        response = await client.wait_for("message", check=lambda
            message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=30)
        if "<#" not in response.content.lower():
            await ctx.send(f"\"{response.content}\" n'est pas un salon")
            return
        id = replaces(response.content, "<#", "", ">", "")
        channel = client.get_channel(int(id))
        dico[ctx.guild.id]["logs"] = channel.id
        dico_update()
        await ctx.send(f"Les logs sont maintenant activées dans {channel.mention} !")
    else:
        dico[ctx.guild.id]["logs"] = None
        dico_update()
        await ctx.send("Les logs sont maintenant désactivées !")


@client.command()
async def view(ctx):
    reponse = await client.wait_for("message", check=lambda
        message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=30)
    print(reponse.content)


# - moi
@client.command(aliases=["set_avatar", "setpp"])
async def set_pp(ctx):
    if ctx.author.id != 236853417681616906:
        return

    if len(ctx.message.attachments) == 0:
        await ctx.send("Il faut envoyer une image")

    elif len(ctx.message.attachments) > 1:
        await ctx.send("Il faut qu'une image")

    else:
        file = ctx.message.attachments[0].filename
        await ctx.message.attachments[0].save(file)
        byte_avatar = open(file, "rb").read()
        try:
            await client.user.edit(avatar=byte_avatar)
        except:
            await ctx.send("Il faut attendre entre chaque changement de pp")
            return
        await ctx.message.add_reaction("✅")
        os.remove(file)


@client.command()
async def shutdown(ctx):
    if ctx.author.id != 236853417681616906:
        return

    await ctx.message.add_reaction("✅")
    await client.close()
    exit()


@client.command()
async def dm(ctx, member, *, msg):
    if ctx.author.id != 236853417681616906:
        return
    member = get_member(member)

    if member is None:
        await ctx.send("Vous n'avez pas mentionné un joueur !")

    await member.send(msg)
    await ctx.message.add_reaction("✅")


@dm.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Le membre n'existe pas ou est introuvable")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque des arguments ! syntaxe: {prefix}dm <membre> <msg>")


@client.command()
async def get_dm(ctx, member):
    if ctx.author.id != 236853417681616906:
        return

    member = get_member(member)

    if member is None:
        await ctx.send("Vous n'avez pas mentionné un joueur !")

    str = ""
    async for message in member.history(limit=None):
        str = message.author.name + ": " + message.content + "\n-----------\n\n"
        await ctx.send(str)


@get_dm.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Le membre n'existe pas ou est introuvable")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque des arguments ! syntaxe: {prefix}dm <membre> <msg>")


# --- logs       
# - message
@client.event
async def on_message_delete(message):
    if dico[message.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"un message de {message.author.name} a été supprimé", icon_url=message.author.avatar_url)
        embed.set_thumbnail(url=get_img("trash"))

        if message.embeds:
            await channel_send(dico[message.guild.id]["logs"]).send(
                content=f"un message avec un embed de **{message.author.name}** à été supprimé\nCe qui à été supprimé est le embed de ce message",
                embed=message.embeds[0])
            return
        else:
            if message.content == "":
                embed.add_field(name="contenu", value="<fichier>", inline=True)
            else:
                embed.add_field(name="contenu", value=message.content, inline=True)

            embed.add_field(name=f"󠀮salon", value=message.channel.mention, inline=True)
            embed.add_field(name="󠀮 ", value=message.author.mention + " - " + get_date_time(), inline=False)
            msg = await channel_send(dico[message.guild.id]["logs"]).send(embed=embed)

        if len(message.attachments) != 0:
            files = []
            for attachment in message.attachments:
                await attachment.save(attachment.filename)
                files.append(attachment.filename)

            for index, file in enumerate(files):
                embed = discord.Embed(color=0xf0a3ff)
                embed.set_author(name=f"un message de {message.author.name} a été supprimé",
                                 icon_url=message.author.avatar_url)
                embed.set_thumbnail(url=get_img("trash"))

                if file.endswith(".mp4"):
                    embed.video.url = f"attachment://{file}"
                    embed.video.height = message.attachments[index]
                    embed.video.width = message.attachments[index]

                elif file.endswith((".png", ".jpg", ".jpeg")):
                    embed.set_image(url=f"attachment://{file}")

                embed.add_field(name=f"󠀮salon", value=message.channel.mention, inline=True)
                embed.add_field(name="󠀮 ", value=message.author.mention + " - " + get_date_time(), inline=False)
                ds_file = discord.File(file)
                await msg.reply(file=ds_file, embed=embed)
                os.remove(file)


@client.event
async def on_message_edit(before, after):
    if before.author.bot or before.guild is None or before.content == after.content:
        return
    if dico[before.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{before.author.name} a modifié un message", icon_url=before.author.avatar_url)
        embed.set_thumbnail(url=get_img("edit"))
        embed.add_field(name="avant", value=before.content, inline=True)
        embed.add_field(name="󠀮salon", value=before.channel.mention, inline=True)
        embed.add_field(name="après", value=after.content, inline=False)
        embed.add_field(name="󠀮 ",
                        value=f"{after.author.mention + ' - ' + get_date_time()} - [link]({before.jump_url})",
                        inline=False)
        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


# - channel
@client.event
async def on_guild_channel_create(channel):
    if dico[channel.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"channel créé", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("plus"))
        embed.add_field(name=f"󠀮salon", value=channel.name, inline=True)
        embed.add_field(name="󠀮 ", value=channel.mention + " - " + get_date_time(), inline=False)
        await channel_send(dico[channel.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_guild_channel_delete(channel):
    if dico[channel.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"channel supprimé", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("trash"))
        embed.add_field(name=f"󠀮salon", value=channel.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_date_time(), inline=False)
        await channel_send(dico[channel.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_guild_channel_update(before, after):
    if before.position != after.position:
        return
    if dico[before.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{after.name} a changé de nom", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("edit"))
        embed.add_field(name="avant", value=before.name, inline=True)
        embed.add_field(name=f"󠀮apres", value=after.name, inline=True)
        embed.add_field(name="󠀮 ", value=after.mention + " - " + get_date_time(), inline=False)
        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


# - role
@client.event
async def on_guild_role_create(role):
    if dico[role.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"un nouveau rôle a été créé", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("plus"))
        embed.add_field(name="nom", value=role.name, inline=True)
        embed.add_field(name="󠀮 ", value=role.mention + " - " + get_date_time(), inline=False)
        await channel_send(dico[role.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_guild_role_update(before, after):
    if before.name == after.name:
        return
    if dico[before.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"le rôle {after.name} a été modifié", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("edit"))
        embed.add_field(name="avant", value=before.name, inline=True)
        embed.add_field(name="après", value=after.name, inline=True)
        embed.add_field(name="󠀮 ", value=after.mention + " - " + get_date_time(), inline=False)
        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_guild_role_delete(role):
    if dico[role.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"le rôle {role} a été supprimer", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("trash"))
        embed.add_field(name="nom", value=role.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_date_time(), inline=False)
        await channel_send(dico[role.guild.id]["logs"]).send(embed=embed)


# - gestion/ban/kick/gens/member
@client.event
async def on_guild_join(guild):
    if guild.id not in dico:
        dico[guild.id] = {"name": guild.name, "logs": None, "voc": None, "autorole": None}
    dico_update()


@client.event
async def on_member_ban(guild, member):
    if dico[guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} a été banni", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("notif"))
        embed.add_field(name="membre", value=member.mention, inline=True)
        embed.add_field(name="󠀮 ", value=get_date_time(), inline=False)
        await channel_send(dico[guild.id]["logs"]).send(embed=embed)


@client.event
async def on_member_unban(guild, member):
    if dico[guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} a été débanni", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("notif"))
        embed.add_field(name="membre", value=member.mention, inline=True)
        embed.add_field(name="󠀮 ", value=get_date_time(), inline=False)
        await channel_send(dico[guild.id]["logs"]).send(embed=embed)


@client.event
async def on_member_join(member):
    if dico[member.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} a rejoint le serveur", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("notif"))
        embed.add_field(name="membre", value=member.mention, inline=True)
        embed.add_field(name="󠀮 ", value=member.mention + " - " + get_date_time(), inline=False)
        await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)
    if dico[member.guild.id]["autorole"] is not None and not member.bot:
        role = discord.utils.get(member.guild.roles, id=dico[member.guild.id]["autorole"])
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            await member.guild.owner.send(f"Je ne peut pas donner le rôle {role.name} à {member.mention}.\nLe rôle Eula doit être plus haut que le rôle {role.name}")
    if dico[member.guild.id]["welcome_msg"] is not None:
        await member.send(dico[member.guild.id]["welcome_msg"].replace("$username$", member.name))


@client.event
async def on_member_remove(member):
    if dico[member.guild.id]["logs"] is not None:
        embed = discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} a quitté le serveur", icon_url=get_img("setting"))
        embed.set_thumbnail(url=get_img("notif"))
        embed.add_field(name="membre", value=member.mention, inline=True)
        embed.add_field(name="󠀮 ", value=get_date_time(), inline=False)
        await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_member_update(before, after):
    if dico[before.guild.id]["logs"] is not None:
        if before.display_name != after.display_name:
            embed = discord.Embed(color=0xf0a3ff)
            embed.set_author(name=f"{before.name} a changé de surnom", icon_url=get_img("setting"))
            embed.set_thumbnail(url=get_img("edit"))
            embed.add_field(name="avant", value=before.display_name, inline=True)
            embed.add_field(name="après", value=after.display_name, inline=True)
            embed.add_field(name="󠀮 ", value=after.mention + " - " + get_date_time(), inline=False)
            await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)

        if before.roles != after.roles:
            if len(before.roles) < len(after.roles):
                for role in after.roles:
                    if role not in before.roles:
                        if role.id != dico[before.guild.id]["voc"]:
                            embed = discord.Embed(color=0xf0a3ff)
                            embed.set_author(name=f"{before.name} a gagné un rôle", icon_url=before.avatar_url)
                            embed.set_thumbnail(url=get_img("plus"))
                            embed.add_field(name="role", value=role.mention, inline=True)
                            embed.add_field(name="󠀮 ", value=after.mention + " - " + get_date_time(), inline=False)
                            await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)

            if len(before.roles) > len(after.roles):
                for role in before.roles:
                    if role not in after.roles:
                        if role.id != dico[before.guild.id]["voc"]:
                            embed = discord.Embed(color=0xf0a3ff)
                            embed.set_author(name=f"{before.name} a perdu un rôle", icon_url=before.avatar_url)
                            embed.set_thumbnail(url=get_img("minus"))
                            embed.add_field(name="role", value=role.mention, inline=True)
                            embed.add_field(name="󠀮 ", value=after.mention + " - " + get_date_time(), inline=False)
                            await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


# - vocal
@client.event
async def on_voice_state_update(member, before, after):
    if dico[member.guild.id]["logs"] is not None:
        if before.channel != after.channel:

            embed = discord.Embed(color=0xf0a3ff)

            if before.channel is None:
                embed.set_author(name=f"{member.name} a rejoint un salon vocal", icon_url=member.avatar_url)
                embed.set_thumbnail(url=get_img("enter"))
                embed.add_field(name=f"󠀮salon", value=after.channel.mention, inline=True)

                if dico[member.guild.id]["voc"] is not None:
                    await member.add_roles(discord.utils.get(member.guild.roles, id=dico[member.guild.id]["voc"]))

            elif after.channel is None:
                embed.set_author(name=f"{member.name} a quitté un salon vocal", icon_url=member.avatar_url)
                embed.set_thumbnail(url=get_img("exit"))
                embed.add_field(name=f"󠀮salon", value=before.channel.mention, inline=True)

                if dico[member.guild.id]["voc"] is not None:
                    await member.remove_roles(discord.utils.get(member.guild.roles, id=dico[member.guild.id]["voc"]))

            else:
                embed = discord.Embed(color=0xf0a3ff)
                embed.set_author(name=f"{member.name} a changé de salon vocal", icon_url=member.avatar_url)
                embed.set_thumbnail(url=get_img("shuffle"))
                embed.add_field(name=f"󠀮avant", value=before.channel.mention, inline=True)
                embed.add_field(name=f"󠀮après", value=after.channel.mention, inline=True)

            embed.add_field(name="󠀮 ", value=member.mention + " - " + get_date_time(), inline=False)
            await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)


client.run(token)
