import asyncio
import ast
import time
import os
import random
import requests

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from keep_alive import keep_alive

#--- dico
dico = ast.literal_eval(open("/home/runner/Eula-bot/server.txt", "r").read().replace("'", '"'))
# forme:  {id: {"name": str, "logs": int, "voc": int, "autorole": int, "welcome_msg": str}}



# --- setup
prefix = "!"
default_intents = discord.Intents.default()
decalage_horaire = 1
default_intents.members = True
client = commands.Bot(command_prefix = [prefix, "<@914226393565499412> ", "<@914226393565499412>"],  help_command = None, intents = default_intents)

print("connection...")


@client.event
async def on_ready():
    print("connecté ! ⊂(◉‿◉)つ")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"{prefix}help"))
    for serveur in client.guilds:
        if serveur.id not in dico:
           dico[serveur.id] =  {"name": serveur.name, "logs": None, "voc": None, "autorole": None}
    open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))

# --- fonctions
# - all
def channel_send(id):
    return client.get_channel(id)


def get_time():
    time_ = str(time.strftime("%d/%m/%Y - %H:%M:%S", time.localtime()))
    hour = time.strftime("%H", time.localtime())
    return time_.replace(hour, str(int(hour) + decalage_horaire))


def replaces(string, *args):
    for i in range(0, len(args), 2):
        string = string.replace(args[i], args[i + 1])
    return string

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
            for reaction in e.reactions:
                if reaction.emoji == "🖐️":
                    async for user in reaction.users():
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
    print("bjk")
    if not member.isdigit():
        member = replaces(id, "<@", "", ">", "")
    print(member)
    member = client.get_user(int(member))
    await ctx.send(f"{member.mention} acceptez-vous la partie de {name_game} contre **{ctx.author.name}** ?")
    try:
        msg = await client.wait_for("message", check=lambda message: message.author.id in [member.id, ctx.author.id] and message.content.lower() in ["y", "o", "n", "yes", "oui", "no", "non"], timeout=180)
    except asyncio.TimeoutError:
        await ctx.reply(f"**{member.name}** n'a pas répondu", mention_author=False)
        return False

    if msg.content.lower() in ["n", "non", "no"]:
        await ctx.send("Partie refusée")
        return False
    else:
        return True


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
        await ctx.send(f"󠀮 \n**Partie finie !**\nLe vainqueur est {username.mention} avec {dico_points[username.id]} points !")
    else:
        str_winner = ""
        for i, e in enumerate(list_winner):
            username = client.get_user(list_winner[i])
            str_winner += " " + username.mention
        await ctx.send(f"󠀮 \n**Partie finie !**\nLes vainqueurs sont {str_winner} avec {dico_points[username.id]} points !")
    

# --- commandes/commands
# - everyone
@client.command()
async def hentai(ctx, category = "help", nbr = "1"):
    if nbr.isdigit():
        nbr = int(nbr)
    else:
        nbr = 1

    if nbr > 20:
        await ctx.send("Le nombre maximum d'image est de 20")
        nbr = 20

    if not ctx.channel.is_nsfw() and not ctx.author.guild_permissions.administrator:
        await ctx.send("Il faut que le salon soit nsfw pour que la commande fonctionne")
        return

    if category in ["ass", "bdsm", "cum", "creampie", "manga", "femdom", "hentai", "incest", "masturbation", "public", "ero", "orgy", "elves", "yuri", "pantsu", "glasses", "cuckold", "blowjob", "boobjob", "foot", "thighs", "vagina", "ahegao", "uniform", "gangbang", "tentacles", "gif", "neko", "nsfwMobileWallpaper", "zettaiRyouiki"]:
        for _ in range(nbr):
            response = requests.get(f"https://hmtai.herokuapp.com/nsfw/{category}")
            link = ast.literal_eval(response.text)
            await ctx.send(link["url"])
    else:
        await ctx.send("**Liste des categories:**\nass, bdsm, cum, creampie, manga, femdom, hentai, incest, masturbation, public, ero, orgy, elves, yuri, pantsu, glasses, cuckold, blowjob, boobjob, foot, thighs, vagina, ahegao, uniform, gangbang, tentacles, gif, neko, nsfwMobileWallpaper, zettaiRyouiki")


@client.command(aliases=["profile_picture", "pdp"])
async def pp(ctx, id):
    if not id.isdigit():
        id = replaces(id, "<@", "", ">", "")

    member = client.get_user(int(id))
    if member is None:
        await ctx.send("Je ne peux pas trouver l'utilisateur !")
    filename = "avatar.gif" if member.is_avatar_animated() else "avatar.png"
    await member.avatar_url.save(filename)
    file = discord.File(fp=filename)
    await ctx.send(file=file)
    os.remove(filename)



@client.command(aliases=["random"])
async def aleatoire(ctx, nbr):
    if int(nbr) < 0 :
        await ctx.send("Le nombre doit être plus grand que 0")
    else:
        await ctx.send(random.randint(0, int(nbr)))


@aleatoire.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque le nombre ! syntaxe: {prefix}random <nombre>")


@client.command(aliases=["8ball", "8"])
async def eightball(ctx, *, msg):
    a = ["Une chance sur deux", "D'après moi oui", "C'est certain", "Oui absolument", "Sans aucun doute", "Très probable", "Oui", "C'est bien parti", "C'est non", "Peu probable", "Faut pas rêver", "N'y compte pas", "Impossible"]
    if msg.endswith("ratio ?"):
        await ctx.reply("ratio !", mention_author=False)
    else:
        await ctx.reply(a[random.randint(0, len(a) - 1)], mention_author=False)


@client.command()
async def ping(ctx):
    embed=discord.Embed(color=0xf0a3ff)
    embed.set_author(name="ping", icon_url="https://media.discordapp.net/attachments/836943322580516904/917794030694318172/padoru_eula___genshin_impact_by_dekunyart_devgso1-fullview.png?width=614&height=614")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/915294111362334810/power-button.png")
    embed.add_field(name="󠀮 ", value="**Je suis connecté !**", inline=True)
    await ctx.send(embed=embed)


@client.command()
async def help(ctx):
    embed=discord.Embed(color=0xf0a3ff)
    embed.set_author(name="help - Eula", icon_url="https://media.discordapp.net/attachments/836943322580516904/917794030694318172/padoru_eula___genshin_impact_by_dekunyart_devgso1-fullview.png?width=614&height=614")
    embed.add_field(name="contact", value="Si vous avez des retours à faire venez DM **kojhyy#0012**\n󠀮 ", inline=False)
    if ctx.author.guild_permissions.administrator:
        embed.add_field(name=f"{prefix}toggle_autorole <role> - _admin_", value="active/desactive le fait de donner un role à tous les nouveaux arrivant", inline=False)
        embed.add_field(name=f"{prefix}toggle_rolevocal - _admin_", value="active/desactive le fait de donner un role à chaque fois qu'un membre rejoint un salon vocal ", inline=False)  
        embed.add_field(name=f"\n{prefix}toggle_logs - _admin_", value="active/désactive les logs", inline=False)
        embed.add_field(name=f"\n{prefix}toggle_welcome_message - _admin_", value="active/désactive le message de bienvenue", inline=False)
        embed.add_field(name=f"{prefix}clear <nbr/texte> - _admin_", value="supprime le nombres de messages,\nsupprime les messages jusqu'au texte donné", inline=False)
        embed.add_field(name=f"{prefix}nuck <salon> - _admin_", value="enleve tous les messages d'un salon", inline=False)
              
        embed.add_field(name=f"{prefix}say <salon> <message> - _admin_", value="envoie un message dans un salon", inline=False)
        embed.add_field(name=f"{prefix}reaction <salon> <id du msg> <reactions>", value="le bot réagit au message avec les reactions donnés, les reaction doivent être coller", inline=False)
        embed.add_field(name=f"{prefix}dm <id du membre/mention> <message>", value="envoie le message avec le bot",inline=False)
    embed.add_field(name="commandes normales", value="----------------------------", inline=False)
    embed.add_field(name=f"{prefix}8ball <message>", value="Boule magique", inline=False)
    embed.add_field(name=f"{prefix}10fastfinger", value="jeu multijoueur dans lequel les participants doivent écrire une phrase le plus vite possible", inline=False)
    embed.add_field(name=f"{prefix}calcul_mental", value="jeu multijoueur dans lequel les participants doivent résoudre des calculs", inline=False)
    embed.add_field(name=f"{prefix}random <nombre>", value="donne un nombre aleatoire entre 0 et le nombre donné", inline=False)
    embed.add_field(name=f"{prefix}ping", value="ping le bot", inline=False)
    embed.add_field(name=f"{prefix}puissance4 <id du membre/mention>", value="lance une partie de puissance 4", inline=False)
    embed.add_field(name=f"{prefix}hentai <categorie> <nbr d'images>", value="si le salon est NSFW envoie des images hentai", inline=False)
    embed.add_field(name=f"{prefix}pp <id du membre/mention>", value="donne la pp du membre", inline=False)
    await ctx.send(embed=embed)
    # embed.add_field(name=f"{prefix}", value="", inline=False)


# - jeux
@client.command(aliases=["10fastfinger", "10ff"])
async def jeu_reaction(ctx, limit = 5):
    list_user, dico_points = await start_game_multi(ctx, limit, "10fastfinger")
    if list_user == []:
        return

    turn = 0
    def get_sentences():
        a = requests.get("https://enneagon.org/phrases").text

        a = a[a.find('<div class="main">') + 23 : a.find("</div>") - 6]
        a = replaces(a, "&nbsp", "", ";" , "", " <br>", "")
        for e in a:
            e = e.replace("É", "E")

        return [i.strip() for e in a.split(".") for i in e.split(",") if 70 > len(i) > 20]

    list_question = get_sentences()
    while turn != limit:
        mot = list_question[random.randint(0, len(list_question) - 1)]
        embed=discord.Embed(color=0xf0a3ff)
        embed.add_field(name="Phrase", value=mot, inline=False)
        await ctx.send(embed=embed)
        list_question.remove(mot)
        if len(list_question) == 0:
            list_question = get_sentences()
        try:
            msg = await client.wait_for("message", check=lambda message: message.author in list_user and message.content in [mot, "exit", "!exit", "leave", "!leave", "Exit", "!Exit", "leave", "Leave"], timeout=60)
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
async def calcul_mental(ctx, limit = 5):
    list_user, dico_points = await start_game_multi(ctx, limit, "calcul mental")
    if list_user == []:
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

        embed=discord.Embed(color=0xf0a3ff)
        embed.add_field(name="Calcul", value=calcul, inline=False)
        await ctx.send(embed=embed)
        try:
            msg = await client.wait_for("message", check=lambda message: message.author in list_user and message.content.lower() in [str(eval(calcul)), "exit", "!exit", "leave", "!leave"], timeout=180)
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


@client.command(aliases=["p4"])
async def puissance4(ctx, member):
    print("sa")
    response = await start_game_duo(ctx, member, "puissance 4")
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
        embed=discord.Embed(color=0x000000, title="Puissance 4")
        embed.add_field(name="Preparation", value="...", inline=False)
        embed.add_field(name="Plateau", value=f"1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n{str_plateau(plateau)}", inline=False)
        msg = await ctx.send(embed=embed)
        for e in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "🔄", "⬇️"]:
            await msg.add_reaction(e)
        return msg

    msg = await send()

    async def edit_embed(title = None, message = None):
        embed=discord.Embed(color=dico_p4[couleur][2], title="Puissance 4")
        embed.add_field(name="Tour de", value=dico_p4[couleur][0].mention, inline=False if title is None else True)
        if title is not None:
            embed.add_field(name=title, value=message, inline=True)
        embed.add_field(name="Plateau", value=f"1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n{str_plateau(plateau)}", inline=False)
        await msg.edit(embed=embed)

    async def end():
        try:
            num, user = await client.wait_for("reaction_add", check=lambda reaction, user: str(reaction.emoji) == "🔄" and user.id in [dico_p4["rouge"][0].id, dico_p4["jaune"][0].id], timeout=30)
        except asyncio.TimeoutError:
            return None
        plateau = [[rond_gris for _ in range(7)] for _ in range(6)]
        await msg.remove_reaction(num.emoji, user)
        return plateau

    while True:
        while plateau[0].count(rond_gris) != 0:
            await edit_embed()
            
            try:
                num, _ = await client.wait_for("reaction_add", check=lambda reaction, user: str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "🔄", "⬇️"] and user.id == dico_p4[couleur][0].id, timeout=180)
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
                    await ctx.send(f"{dico_p4[couleur][0].mention} la colonne {dict_number[num.emoji] + 1} est pleine !")
                else:

                    listex = plateau[positionx]
                    listey = [plateau[i][positiony] for i in range(6)]

                    listeDiago1 = [plateau[positionx - i][positiony - i] for i in range(0, 7) if positionx - i >= 0 and positiony - i >= 0]
                    listeDiago1.reverse()
                    listeDiago1 += [plateau[positionx + i][positiony + i] for i in range(1, 7) if positiony + i < 7 and positionx + i < 6]
                    listeDiago1.reverse()

                    listeDiago2 = [plateau[positionx - i][positiony + i] for i in range(0, 7) if positionx - i >= 0 and positiony + i <= 6]
                    listeDiago2.reverse()
                    listeDiago2 += [plateau[positionx + i][positiony - i] for i in range(1, 7) if positionx + i < 6 and positiony - i >= 0]
                    listeDiago2.reverse()

                    for liste in [listex, listey, listeDiago1, listeDiago2]:
                        tmp = "".join(liste)
                        if tmp.count(dico_p4[couleur][1]) != tmp.replace(dico_p4[couleur][1] * 4, "").count(dico_p4[couleur][1]):
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
        await ctx.send(f"Il manque le membre a affronter ! syntaxe: {prefix}puissance4 <membre>")

# - admin
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
        await ctx.send("L'id correspond à auncun message ou le bot ne peux pas mettre la reaction saisie")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque des arguments ! syntaxe: {prefix}reaction <salon> <id du msg> <reactions>")


@client.command()
async def dm(ctx, id, *, msg):
    if not id.isdigit():
        id = replaces(id, "<@!", "", ">", "")

    member = client.get_user(int(id))
    await member.send(msg + f"\n\nmessage envoyé par {ctx.author.mention}")
    await ctx.message.add_reaction("✅")

@dm.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Le membre n'existe pas ou est introuvable")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque des arguments ! syntaxe: {prefix}dm <membre> <msg>")


@client.command()
@has_permissions(administrator=True)
async def toggle_welcome_message(ctx, msg = None):
    if dico[ctx.guild.id]["welcome_msg"] is None:
        if msg is None:
            await ctx.send(f"**quel message de bienvenue voulez-vous mettre ?**\npour que le bot écrive le nom du nouvel arrivant dans message écriver $username$\nexemple: le message \"bienvenue $username$\" donnera \"bienvenue {ctx.author.name}\"")
            response = await client.wait_for("message", check=lambda message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=180)
            msg = response.content
        dico[ctx.guild.id]["welcome_msg"] = msg
        open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
        await ctx.send("le nouveau message de bienvenue est enregistré")
    else:
        await ctx.send(f"Le message actuel est \n\n\"{dico[ctx.guild.id]['welcome_msg']}\" \n\nVoulez-vous désactivé le message de bienvenue ?")
        response = await client.wait_for("message", check=lambda message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id and message.content.lower() in ["o", "oui", "yes", "y", "no", "n", "non"], timeout=180)
        if response.content.lower() in ["o", "oui", "yes", "y"]:
            dico[ctx.guild.id]["welcome_msg"] = None
            open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
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
async def toggle_autorole(ctx, role : discord.Role = None):
    if dico[ctx.guild.id]["autorole"] is None:
        if role is None:
            await ctx.send("quel role voulez vous mettre ?")
            response = await client.wait_for("message", check=lambda message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=30)
            if "<@&" not in response.content.lower():
                await ctx.send(f"\"{response.content}\" n'est pas un rôle")
                return
            id = replaces(response.content, "<@&", "", ">", "")
            role = discord.utils.get(ctx.author.guild.roles, id=int(id))
        dico[ctx.guild.id]["autorole"] = role.id
        open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
        await ctx.send(f"Le role {role.mention} est maintenant donné à tous les nouveaux arrivant !")
    else:
        dico[ctx.guild.id]["autorole"] = None
        open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
        await ctx.send("La fonction d'autorole est maintenant désactivé")


@client.command(aliases=["c"])
@has_permissions(administrator=True)
async def clear(ctx, *, arg = "1"):
    if arg.isdigit():
        await ctx.channel.purge(limit = int(arg) + 1)
    else:
        tmp = 0
        async for message in ctx.history(limit = 500):
            tmp += 1
            if message.content == arg:
                await ctx.send(f"{tmp - 2} messages sélectionner jusqu'à \"{arg}\". voulez-vous les supprimer ? (oui/non)")
                msg = await client.wait_for("message", check = lambda message: message.author == ctx.author)
                if msg.content.lower() in ["oui", "o", "y", "yes"]:
                    await ctx.channel.purge(limit = tmp + 1)
                else:
                    await msg.add_reaction("✅")
                return


@client.command()
@has_permissions(administrator=True)
async def nuck(ctx, channel):
    if not channel.isdigit():
        channel = replaces(channel, "<#", "", ">", "")

    channel = client.get_channel(int(channel))
    if channel is None:
        await ctx.send("salon non trouvé")
        return
    
    await ctx.send(f"Voulez-vous vraiment nuck le salon {channel.mention} ?")
    try:
        reponse = await client.wait_for("message", check=lambda message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout = 30)
    except asyncio.TimeoutError:
        await ctx.send("délai dépassé")
        return
    if reponse.content.lower() in ["yes", "y", "o", "oui"]:
        await ctx.guild.create_text_channel(channel.name, overwrites = channel.overwrites, category = channel.category, position = channel.position, topic = channel.topic, nsfw = channel.nsfw, slowmode_delay = channel.slowmode_delay)
        await channel.delete()
        await ctx.send("Channel nuck !")

@nuck.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque le salon ! syntaxe: {prefix}nuck <salon>")

@client.command()
@has_permissions(administrator=True)
async def toggle_rolevocal(ctx, role: discord.Role):
    if dico[ctx.author.guild.id]["voc"] is None:
        if role is None:
            await ctx.send("quel role voulez vous mettre ?")
            response = await client.wait_for("message", check=lambda message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=30)
            if "<@&" not in response.content.lower():
                await ctx.send(f"\"{response.content}\" n'est pas un rôle")
                return
            id = replaces(response.content, "<@&", "", ">", "")
            role = discord.utils.get(ctx.author.guild.roles, id=int(id))
        dico[ctx.guild.id]["autorole"] = role.id
        open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
        await ctx.send(f"Le role {role.mention} est maintenant donné à toutes les personnes qui rentre dans un salon vocal !")
    else:
        dico[ctx.author.guild.id]["voc"] = None
        open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
        await ctx.send("Plus aucun role ne sera donner quand quelqu'un rejoint un salon vocal")


@client.command()
@has_permissions(administrator=True)
async def toggle_logs(ctx, channel = None):
    if dico[ctx.author.guild.id]["logs"] is None:
        if channel is None:
            await ctx.send("Dans quel salon voulez-vous activés les logs ?")
            response = await client.wait_for("message", check=lambda message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout=30)
            if "<#" not in response.content.lower():
                await ctx.send(f"\"{response.content}\" n'est pas un salon")
                return
            id = replaces(response.content, "<#", "", ">", "")
            channel = client.get_channel(int(id))
        dico[ctx.guild.id]["logs"] = channel.id
        open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
        await ctx.send(f"Les logs sont maintenant activés dans {channel.mention} !")
    else:
        dico[ctx.guild.id]["logs"] = None
        open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
        await ctx.send("Les logs sont maintenant désactivé !")


@client.command()
async def view(ctx):
    reponse = await client.wait_for("message", check=lambda message: message.author.id == ctx.author.id and ctx.channel.id == message.channel.id, timeout = 30)
    print(reponse.content)


# - moi
@client.command(aliases=["set_avatar"])
async def set_pp(ctx):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Il faut envoyé une image")
    elif len(ctx.message.attachments) > 1:
        await ctx.send("Il faut qu'une image")
    else:
        file = ctx.message.attachments[0].filename
        await ctx.message.attachments[0].save(file)
        byte_avatar = open(file, "rb").read()
        await client.user.edit(avatar=byte_avatar)
        await ctx.message.add_reaction("✅")
        os.remove(file)


        
# --- logs       
# - message
@client.event
async def on_message_delete(message):
    if message.author.bot:
        return
    if dico[message.guild.id]["logs"] is not None:
        if message.attachments == []:
            embed=discord.Embed(color=0xf0a3ff)
            embed.set_author(name=f"{message.author.name} à supprimé un message", icon_url=message.author.avatar_url)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/836943322580516904/914539782040850472/unknown.png")
            embed.add_field(name="contenu", value=message.content, inline=True)
            embed.add_field(name=f"󠀮salon", value=message.channel.mention, inline=True)
            embed.add_field(name="󠀮 ", value=message.author.mention + " - " + get_time(), inline=False)
            await channel_send(dico[message.guild.id]["logs"]).send(embed=embed)
        else:
            files = []
            for attachment in message.attachments:
                await attachment.save(attachment.filename)
                files.append(attachment.filename)

            for file in files:
                embed=discord.Embed(color=0xf0a3ff)
                embed.set_author(name=f"{message.author.name} à supprimé un message", icon_url=message.author.avatar_url)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/836943322580516904/914539782040850472/unknown.png")
                if message.content == "":
                    embed.add_field(name="contenu", value="<image>", inline=True)
                else:
                    embed.add_field(name="contenu", value=message.content, inline=True)
                embed.set_image(url=f"attachment://{file}")
                embed.add_field(name=f"󠀮salon", value=message.channel.mention, inline=True)
                embed.add_field(name="󠀮 ", value=message.author.mention + " - " + get_time(), inline=False)
                ds_file = discord.File(file)
                await channel_send(dico[message.guild.id]["logs"]).send(file=ds_file, embed=embed)
                os.remove(file)

@client.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    elif before.content == after.content:
        return
    if dico[before.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{before.author.name} à modifié un message", icon_url=before.author.avatar_url)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914861144206893076/edit.png")
        embed.add_field(name="avant", value=before.content, inline=True)
        embed.add_field(name="󠀮salon", value=before.channel.mention, inline=True)
        embed.add_field(name="après", value=after.content, inline=False)
        embed.add_field(name="󠀮 ", value=f"{after.author.mention + ' - '  + get_time()} - [link]({before.jump_url})", inline=False)
        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


# - channel
@client.event
async def on_guild_channel_create(channel):
    if dico[channel.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"channel créé", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914918043170259074/plus_1.png")
        embed.add_field(name=f"󠀮salon", value=channel.name, inline=True)
        embed.add_field(name="󠀮 ", value=channel.mention + " - " + get_time(), inline=False)
        await channel_send(dico[channel.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_guild_channel_delete(channel):
    if dico[channel.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"channel supprimé", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/836943322580516904/914539782040850472/unknown.png")
        embed.add_field(name=f"󠀮salon", value=channel.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[channel.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_guild_channel_update(before , after):
    if before.position != after.position:
        return
    if dico[before.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{after.name} à changé de nom", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914861144206893076/edit.png")
        embed.add_field(name="avant", value=before.name, inline=True)
        embed.add_field(name=f"󠀮apres", value=after.name, inline=True)
        embed.add_field(name="󠀮 ", value=after.mention + " - " + get_time(), inline=False)
        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


# - role
@client.event
async def on_guild_role_create(role):
    if dico[role.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"un nouveau role à été créé", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914918043170259074/plus_1.png")
        embed.add_field(name="nom", value=role.name, inline=True)
        embed.add_field(name="󠀮 ", value=role.mention + " - " + get_time(), inline=False)
        await channel_send(dico[role.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_guild_role_update(before, after):
    if before.name == after.name:
        return
    if dico[before.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"le role {after.name} à été modifié", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914861144206893076/edit.png")
        embed.add_field(name="avant", value=before.name, inline=True)
        embed.add_field(name="après", value=after.name, inline=True)
        embed.add_field(name="󠀮 ", value=after.mention + " - " + get_time(), inline=False)
        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_guild_role_delete(role):
    if dico[role.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"le role {role} à été supprimer", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914539782040850472/unknown.png")
        embed.add_field(name="nom", value=role.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[role.guild.id]["logs"]).send(embed=embed)


# - gestion/ban/kick/gens/member
@client.event
async def on_guild_join(guild):
    if guild.id not in dico:
           dico[guild.id] =  {"name": guild.name, "logs": None, "voc": None, "autorole": None}
    open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))


@client.event
async def on_member_ban(guild, member):
    if dico[guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} à été banni", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914883218275205160/notifications.png")
        embed.add_field(name="membre", value=member.mention, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[guild.id]["logs"]).send(embed=embed)


@client.event
async def on_member_unban(guild, member):
    if dico[guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} à été débanni", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914883218275205160/notifications.png")
        embed.add_field(name="membre", value=member.mention, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[guild.id]["logs"]).send(embed=embed)


@client.event
async def on_member_join(member):
    if dico[member.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} à rejoint le serveur", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914883218275205160/notifications.png")
        embed.add_field(name="membre", value=member.mention, inline=True)
        embed.add_field(name="󠀮 ", value=member.mention + " - " + get_time(), inline=False)
        await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)
    if dico[member.guild.id]["autorole"] is not None and not member.bot:
        role = discord.utils.get(member.guild.roles, id = dico[member.guild.id]["autorole"])
        await member.add_roles(role)
    if dico[member.guild.id]["welcome_msg"] is not None:
        await member.send(dico[member.guild.id]["welcome_msg"].replace("$username$", member.name))

        
@client.event
async def on_member_remove(member):
    if dico[member.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} à quitté le serveur", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914883218275205160/notifications.png")
        embed.add_field(name="membre", value=member.mention, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_member_update(before, after):
    if dico[before.guild.id]["logs"] is not None:
        if before.display_name != after.display_name:
            embed=discord.Embed(color=0xf0a3ff)
            embed.set_author(name=f"{before.name} à changé de surnom", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914861144206893076/edit.png")
            embed.add_field(name="avant", value=before.display_name, inline=True)
            embed.add_field(name="après", value=after.display_name, inline=True)
            embed.add_field(name="󠀮 ", value=after.mention + " - " + get_time(), inline=False)
            await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)
        if before.roles != after.roles:
            def diff(a, b):
                return [index for index, i in enumerate(a) if i not in b]

            if len(before.roles) < len(after.roles):
                i = diff(after.roles, before.roles)
                for e in i:
                    if after.roles[e].id != dico[before.guild.id]["voc"]:
                        embed=discord.Embed(color=0xf0a3ff)
                        embed.set_author(name=f"{before.name} à gagner un role", icon_url=before.avatar_url)
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914918043170259074/plus_1.png")
                        embed.add_field(name="role", value=after.roles[e].mention, inline=True)
                        embed.add_field(name="󠀮 ", value=after.mention + " - " + get_time(), inline=False)
                        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)
            else:
                i = diff(before.roles, after.roles)
                for e in i:
                    if before.roles[e].id != dico[before.guild.id]["voc"]:
                        embed=discord.Embed(color=0xf0a3ff)
                        embed.set_author(name=f"{before.name} à perdu un role", icon_url=before.avatar_url)
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914918042981498910/minus.png")
                        embed.add_field(name="role", value=before.roles[e].mention, inline=True)
                        embed.add_field(name="󠀮 ", value=after.mention + " - " + get_time(), inline=False)
                        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


# - vocal
@client.event
async def on_voice_state_update(member, before, after):
    if dico[member.guild.id]["logs"] is not None:
        if before.channel != after.channel:
            if before.channel is None:
                embed=discord.Embed(color=0xf0a3ff)
                embed.set_author(name=f"{member.name} à rejoint un salon vocal", icon_url=member.avatar_url)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914539760150806528/unknown.png")
                embed.add_field(name=f"󠀮salon", value=after.channel.mention, inline=True)
                embed.add_field(name="󠀮 ", value=member.mention + " - " + get_time(), inline=False)
                await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)
                if dico[member.guild.id]["voc"] is not None:
                    await member.add_roles(discord.utils.get(member.guild.roles, id = dico[member.guild.id]["voc"]))
            elif after.channel is None:
                embed=discord.Embed(color=0xf0a3ff)
                embed.set_author(name=f"{member.name} à quitté un salon vocal", icon_url=member.avatar_url)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914539761794961458/unknown.png")
                embed.add_field(name=f"󠀮salon", value=before.channel.mention, inline=True)
                embed.add_field(name="󠀮 ", value=member.mention + " - " + get_time(), inline=False)
                await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)
                if dico[member.guild.id]["voc"] is not None:
                    await member.remove_roles(discord.utils.get(member.guild.roles, id = dico[member.guild.id]["voc"]))
            else:
                embed=discord.Embed(color=0xf0a3ff)
                embed.set_author(name=f"{member.name} à changer de salon vocal", icon_url=member.avatar_url)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914922944000577536/shuffle.png")
                embed.add_field(name=f"󠀮avant", value=before.channel.mention, inline=True)
                embed.add_field(name=f"󠀮après", value=after.channel.mention, inline=True)
                embed.add_field(name="󠀮 ", value=member.mention + " - " + get_time(), inline=False)
                await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)


keep_alive()
client.run(os.environ['token'])