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
dico = ast.literal_eval(open("/home/runner/Eula-bot/server.txt", "r").read().replace("f'", '"'))
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
    new_h = "0" if str(int(hour) + decalage_horaire) == "24" else str(int(hour) + decalage_horaire)
    
    return time_.replace(hour, new_h)


def replaces(string, *args):
    for i in range(0, len(args), 2):
        string = string.replace(args[i], args[i + 1])
    return string

def get_member(member):
    if not member.isdigit():
        if "!" in member:
            member = replaces(member, "<@!", "", ">", "")
        else:
            member = replaces(member, "<@", "", ">", "")
    return client.get_user(int(member))
    
    
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
    member = get_member(member)
    
    await ctx.send(f"{member.mention} acceptez-vous la partie de {name_game} contre **{ctx.author.name}** ?")
    try:
        msg = await client.wait_for("message", check=lambda message: message.author.id in [member.id, ctx.author.id] and message.content.lower() in ["y", "o", "n", "yes", "oui", "no", "non"], timeout=180)
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
async def pp(ctx, member):
    member = get_member(member)
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
        embed.add_field(name=f"{prefix}clear <nbr/texte> - _admin_", value="supprime le nombres de messages,\nsupprime les messages jusqu'au lien donné", inline=False)
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
    embed.add_field(name=f"{prefix}monopoly", value="lance une partie de monopoly", inline=False)
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

@client.command()
async def monopoly(ctx):
    # fait une liste de tout les participants
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

    random.shuffle(list_user)  

    class joueur:
        def __init__(self, id: int, mention, name: str, emote) -> None:
            self.id = id
            self.mention = mention
            self.proprietes = []
            self.name = name
            self.argent = 2000
            self.chance = []
            self.prison_ = 0
            self.position = 0
            self.last_position = (12, 11)
            self.emote = emote
            self.sorti_prison = False
            self.gare = 0

        def prison(self):
            self.position = 10
            self.prison = 2

        def deplace(self, valeur):
            """déplace le joueur de la valeur donné

            Args:
                valeur (int): nombre
            """
            tmp = self.position
            self.position = self.position + valeur - 40 if self.position + valeur >= 40 else self.position + valeur
            if self.position < tmp:
                self.argent += 100
            

        def achete(self, propriete):
            """le joueur achete une propriete

            Args:
                propriete (_type_): objet propriete
            """

            self.proprietes.append(propriete)
            self.argent -= propriete.valeur
            propriete.est_achete(self)
            plateau.propriete_acheté(propriete)

        def echange(self, propriete, joueur, prix) -> bool:
            """self échange une propriete avec joueur
                self donne l'argent et joueur donne la propriete

            Args:
                propriete (_type_): la propriete a transfere d'un joueur a l'autre
                joueur (_type_): le joueur avec qui faire la transaction
                prix (_type_): prix de la propriete convenu entre self et joueur

            Returns:
                int: 0 = pas assez d'argent / 1 = joueur n'a pas la propriete / 2 = ok
            """
            if self.argent - prix < 0:
                return 0
            elif propriete not in joueur.proprietes:
                return 1
            else:
                self.argent -= prix
                propriete.est_achete(self)
                joueur.argent += prix
                return 2

        def perd_propriete(self, propriete):
            """self perds la propriete et elle est ajouter dans la liste des propriete libres

            Args:
                propriete (_type_): propriete a enlever
            """
            self.proprietes.remove(propriete)
            plateau.propriete_vendu(propriete)

        def hypotheque(self, propiete):
            """self perds la propriete et gagne la moitié de la valeur de la propriete

            Args:
                propiete (_type_): propriete a hypothéqué 
            """
            self.argent += propiete.valeur * 0.5
            self.perd_propriete(propriete)

        def perd(self):
            liste_joueurs.remove(user)
            for propriete in self.proprietes:
                self.perd_propriete(propriete)
                
            for y in range(len(plateau_matrice)):
                for x in range(len(plateau_matrice)):
                    if plateau_matrice[x][y] == self.emote:
                        plateau_matrice[x][y] = "⬛"

    
    class gare:
        def __init__(self, valeurs: tuple) -> None:
            self.nom = valeurs[0]
            self.num = valeurs[1]
            self.valeur = valeurs[2]
            self.proprietaire = valeurs[3]
            self.loyer = 100
            self.emote = "🚉"
        
        def affiche(self):
            return f"la gare {self.nom} vaut {self.prix} le proprietaire est {self.proprietaire}"

        def est_achete(self, joueur: joueur):
            """change le proprietaire de la propriete
            """
            self.proprietaire = joueur

    
    class propriete:
        def __init__(self, valeurs: tuple) -> None:
            self.nom = valeurs[0]
            self.valeur = valeurs[1]
            self.proprietaire = valeurs[2]
            self.emote = valeurs[3]

        def est_achete(self, joueur: joueur):
            """change le proprietaire de la propriete
            """
            self.proprietaire = joueur
        
        def affiche(self):
            return f"{self.nom} vaut {self.valeur}, le proprietaire est {self.proprietaire}"

    
    class impots:
        def __init__(self, valeurs) -> None:
            self.valeur = valeurs[0]
            self.nom = valeurs[1]
        
        def affiche(self):
            return f"{self.nom}, il faut payer {self.valeur}"

    
    class special:
        def __init__(self, type) -> None:
            self.type = type

        def affiche(self):
            return self.type

        
    def chance(user):
        nbr = random.randint(1, 21)
        if nbr == 1:
            user.position = 0
            user.argent += 100
            return "Retournez à la case départ et touchez 100 ₿"
        elif nbr == 2:
            msg = "Un furry vous pourchasse vous allez au parc gratuit"
            if user.position >= 21:
                user.argent += 100
                msg += "\nvous passez par la case départ et recevez 100 ₿"
            user.position = 0
            return msg
        elif nbr == 3:
            user.argent -= 40
            return "Vous avez gagné un iphone 13 !\nmais c'était une arnaque -40 ₿"
        elif nbr == 4:
            user.position = random.randint(0, 40)
            return "Blitzcrank vous à attrapé, il vous téléporte aléatoirement sur le plateau"
        elif nbr == 5:
            for joueur in liste_joueurs:
                user.argent += 20
                joueur.argent -= 20
            return "C'est ton anniv Bro!!! les autres joueurs doivent te donner de la thune or Konsékens"
        elif nbr == 6:
            user.argent += 100
            return "SIUUUUUU ! Oh mon dieu Ronaldo viens vous voir et vous donne 100 ₿"
        elif nbr == 7:
            user.argent = int(user.argent * 0.95)
            return "Les gros rats de la banque vous vole 5% de votre richesse"
        elif nbr == 8:
            user.argent += 75
            return "Tu es très beau donc tu gagne une concours de beauté >u<. Tu gagne 75 ₿"
        elif nbr == 9:
            user.argent -= 100
            return "Tu as perdu une battle de rap contre JUL... le monde te desteste maintenant et ta famille te renies... -100 ₿"
        elif nbr == 10:
            user.argent -= 200
            return "OMG banner de Klee ! perd 200 ₿. sad ta pity sur Qiqi"
        elif nbr == 11:
            user.argent -= 30
            return "Tu as perdu ton porte feuille... 30 Balles en moins. T'es trop con aussi bro"
        elif nbr == 12:
            user.argent += 125
            return "Tu vends tes pieds sur Onlyfans https://www.onlyfans.com/nokiiro, + 125 ₿"
        elif nbr == 13:
            user.argent -= 175
            return "Tu as trop rager sur Clash royal tu as casse ton téléphone, il faut te le repayer, - 175 ₿"
        elif nbr == 14:
            user.argent += 200
            return "tony a arrêté d'être gay, tu perds moins d'argent en capote, gagne 200 ₿"
        elif nbr == 15:
            user.argent += 175
            return "tu as gagner au loto, o_0 + 175 ₿"
        elif nbr == 16:
            user.argent += 300
            user.prison()
            return "Tu écris le meilleur hentai de loli, gagne 300 mais perds ta santée mentale et va en prison"
        elif nbr == 17:
            user.argent += 125
            return "Tu touches l'héritage de tonton jean-ma, gagne 125 ₿"
        elif nbr == 18:
            user.argent += 100
            return "Tu as gagner au loto mais ton père à enfin fini d'acheter des clopes donc au lieu de gagner 1000 ₿ tu gagne 100 ₿"
        elif nbr == 19:
            propriete_ = plateau.propriete_restante[13]
            print(propriete_)
            print(propriete_.proprietaire)
            print(propriete_.nom)
            msg = "Tu deviens premier ministre des randoms, acquière l'avenue matignon"
            if propriete_.proprietaire is None:
                user.achete(propriete_)
            else:
                propriete_.proprietaire -= propriete_.valeur
                msg += f", si déjà occupée,\nle propriétaire te doit le prix d'acquisition donc {propriete_.proprietaire} paye"
            user.argent += propriete_.valeure
            return msg
        elif nbr == 20:
            user.argent -= 250
            return "tu es mort. tu doit payer 250 ₿ pour pouvoir t'enterrer"
        elif nbr == 21:
            user.argent -= 100
            return "la littérature française t'a aider a avancer ! +10 point en intelligence mais -100€ pour tous les livres acheté"


    class plateau_:
        def __init__(self, liste_cases) -> None:
            propriete_restante = [case for case in liste_cases if isinstance(case, (propriete, gare))]

            self.propriete_restante = propriete_restante
            self.dico_personne_meme_case = {}

        def propriete_acheté(self, propriete):
            """enleve la propriete des proprietes libres

            Args:
                propriete (_type_): propriete qui est acheté
            """
            self.propriete_restante.remove(propriete)

        def propriete_vendu(self, propriete):
            """ajoute la propriete aux proprietes libres

            Args:
                propriete (_type_): propriete qui est vendu
            """
            self.propriete_restante.append(propriete)


    liste_cases = []
    for valeurs in [["départ"], ["boulevard de belleville", 60, None, ":brown_square:"], [chance], ["rue lecoubre", 60, None, ":brown_square:"], [200, "impôts sur le revenue"], ["gare monparnasse", 1, 200, None], ["rue de vaugirard", 100, None, "🟦"], [chance], ["rue de courcelles", 100, None, "🟦"], ["avenue de la republique", 120, None, "🟦"], ["prison"], ["boulevard de la vilette", 140, None, "🟪"], [chance], ["avenue de neuilly", 140, None, "🟪"], ["rue de paradis", 160, None, "🟪"], ["gare de Lyon", 2, 200, None], ["avenue mozart", 180, None, "🟧"], [chance], ["boulevard saint-michel", 180, None, "🟧"], ["place pigalle", 200, None, "🟧"], ["parc gratuit"], ["avenue matignon", 220, None, "🟥"], [chance], ["boulevard malesherbes", 220, None, "🟥"], ["avenue henri-martin", 240, None, "🟥"], ["gare du nord", 3, 200, None], ["faurbourg saint-honoré", 260, None, "🟨"], ["place de la bourse", 260, None, "🟨"], [chance], ["rue la fayette", 280, None, "🟨"], ["allez en prison"], ["avenue de breteuil", 300, None, "🟩"], ["avenue foch", 300, None, "🟩"], [chance], ["boulevard des capucines", 320, None, "🟩"], ["gare de saint-Lazare", 4, 200, None], [chance], ["avenue des champs-élysées", 350, None, "⬜"], [100, "taxe de luxe"], ["rue de la paix", 400, None, "⬜"]]:
        if len(valeurs) == 4 and str(type(valeurs[2])) == "<class 'int'>":
            liste_cases.append(gare(valeurs))
        elif len(valeurs) == 4:
            liste_cases.append(propriete(valeurs))
        elif len(valeurs) == 2:
            liste_cases.append(impots(valeurs))
        elif len(valeurs) == 1 and str(type(valeurs[0])) == "<class 'str'>":
            liste_cases.append(special(valeurs[0]))
        elif len(valeurs) == 1:
            liste_cases.append(valeurs)

    plateau = plateau_(liste_cases)

    plateau_matrice = [
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


    def affiche():
        msg = ""
        for list_of_emote in plateau_matrice:
            for emote in list_of_emote:
                msg += emote
            msg += "\n"
        return msg


    def emote_(tupl, user):
        pos = plateau_matrice[tupl[0]][tupl[1]]
        if pos in liste_emote:
            for user_bis in liste_joueurs:
                if user_bis.emote == pos:
                    plateau.dico_personne_meme_case[tupl] = [user_bis, user]
                    plateau_matrice[tupl[0]][tupl[1]] = "2️⃣"
        elif tupl in plateau.dico_personne_meme_case:
            plateau.dico_personne_meme_case[tupl] = plateau.dico_personne_meme_case[tupl] + [user]
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
            plateau_matrice[tupl[0]][tupl[1]] = dico[len(plateau.dico_personne_meme_case[tupl])]
        else:
            plateau_matrice[tupl[0]][tupl[1]] = user.emote


    def _emote(tupl, user):
        if tupl in plateau.dico_personne_meme_case:
            if len(plateau.dico_personne_meme_case[tupl]) == 2:
                plateau.dico_personne_meme_case[tupl].remove(user)
                plateau_matrice[tupl[0]][tupl[1]] = plateau.dico_personne_meme_case[tupl][0].emote
                plateau.dico_personne_meme_case.pop(tupl, None)
            else:
                plateau.dico_personne_meme_case[tupl].remove(user)
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

                plateau_matrice[tupl[0]][tupl[1]] = dico[len(plateau.dico_personne_meme_case[tupl])]
        else:
            plateau_matrice[tupl[0]][tupl[1]] = "⬛"



    def places_joueurs(user):
        pos = user.position
        _emote(user.last_position, user)

        if 0 <= pos <= 10:
            emote_((12, 11 - pos), user)
            user.last_position = (12, 11 - pos)
        elif 11 <= pos <= 20:
            pos -= 10
            emote_((11 - pos, 0), user)
            user.last_position = (11 - pos, 0)
        elif 21 <= pos <= 30:
            pos -= 20
            emote_((0, 1 + pos), user)
            user.last_position = (0, 1 + pos)
        else:
            pos -= 31
            emote_((2 + pos, 12), user)
            user.last_position = (2 + pos, 12)


    def discord_embed(username, de, action):
        embed=discord.Embed()
        embed.add_field(name="Plateau", value=affiche(), inline=True)
        embed.add_field(name="Tour de", value=username, inline=False)
        embed.add_field(name="dé", value=de, inline=False)
        embed.add_field(name="action", value=action, inline=False)
        return embed


    async def joue(user):

        # lance le dé et déplace le joueur
        await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", "lancement du dé...", "..."))
        de = random.randint(2, 12)
        user.deplace(de)
        places_joueurs(user)

        # prends la case sur laquelle le joueur c'est arreté
        tmp_case = liste_cases[user.position]

        # si la case est une gare ou une propriete
        if isinstance(tmp_case, (propriete, gare)):
            # si le joueur est chez lui il se passe rien 
            if tmp_case.proprietaire == user:
                return
            
            # si le joueur peut acheter la case
            elif tmp_case.valeur < user.argent and tmp_case.proprietaire is None:
                await demande_acheter(user, tmp_case, de)

            # si le joueur doit payer le proprietaire
            elif tmp_case.proprietaire is not None:
                multiplicateur = tmp_case.proprietaire.gare if isinstance(tmp_case, gare) else 1
                if tmp_case.valeur * multiplicateur < user.argent:
                    tmp_case.proprietaire.argent += tmp_case.valeur * multiplicateur
                    user.argent -= tmp_case.valeur * multiplicateur
                    await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", f"**{user.name}** paye {tmp_case.valeur * multiplicateur} à **{tmp_case.proprietaire.name}**"))
                else:
                    await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", f"**{user.name}** ne peut pas payer !\nil est donc éliminer"))
                    user.perd()

            # si le joueur n'a pas assez d'argent
            else:
                await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", "vous n'avez pas assez d'argent pour acheter la propriete"))

        # si la case est une case spécial 
        elif isinstance(tmp_case, special):
            if tmp_case.type == "prison":
                await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", "vous visitez la prison, c'est le repère des arabes"))
            elif tmp_case.type == "parc gratuit":
                await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", "vous visitez le parc gratuit, il y a plein de sdf par terre"))
            elif tmp_case.type == "allez en prison":
                user.prison()
                await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", "le policier vous à pris pour un noir et vous envoye en prison"))

            places_joueurs(user)

        # si la case est une case impots
        elif isinstance(tmp_case, impots):
            await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", f"Vous devez payez les {tmp_case.nom}, {tmp_case.valeur} ₿"))
            
            if tmp_case.valeur < user.argent:
                user.argent -= tmp_case.valeur
            else:
                await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", f"**{user.name}** ne peut pas payer !\nil est donc éliminer"))
                user.perd()

        # si c'est une case chance
        else:
            # lance la fonction chance
            text = chance(user)
            await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", text))
            places_joueurs(user)
            await asyncio.sleep(3)



    async def demande_acheter(user, tmp_case, de):
        await msg.remove_reaction("ℹ️", client.user)
        await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", f"**{user.name}**, voulez-vous acheter \"{tmp_case.nom}\"\npour la somme de {tmp_case.valeur} ₿ ?"))

        try:
            for emote in ["✅", "❌"]:
                await msg.add_reaction(emote)
        except:
            await msg.clear_reactions()
            for emote in ["✅", "❌"]:
                await msg.add_reaction(emote)

        try:
            num, _ = await client.wait_for("reaction_add", check=lambda reaction, user_: user_.id == user.id and str(reaction.emoji) in ["✅", "❌"], timeout=300)
        except asyncio.TimeoutError:
            pass
        else:
            if str(num.emoji) == "✅":
                user.achete(tmp_case)
                if isinstance(tmp_case, gare):
                    print("+ 1 gare")
                    print(user.gare)
                    user.gare += 1
                    print(user.gare)
                await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", f"**{user.name}** vous avez acheté {tmp_case.nom} !"))
            else:
                await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"le dé est tombé sur ... {de} !", f"**{user.name}** vous n'avez pas acheté {tmp_case.nom} !"))

        await msg.clear_reactions()
        for e in ["🎲", "ℹ️"]:
            await msg.add_reaction(e)

    prepa_emote = ["💤", "🦑", "🦥", "♿", "🛒", "👑", "☃️"]
    liste_emote = []
    
    def random_emote():
        tmp = random.choice(prepa_emote)
        prepa_emote.remove(tmp)
        liste_emote.append(tmp)
        return tmp

    liste_joueurs = [joueur(user.id, user.mention, user.name, random_emote()) for user in list_user]

    embed=discord.Embed()
    for joueur_ in liste_joueurs:
        embed.add_field(name=joueur_.name, value=joueur_.emote, inline=True)
    await ctx.send(embed=embed)
     
    msg = await ctx.send(embed=discord_embed("...", "...", "..."))
    for e in ["🎲", "ℹ️"]:
        await msg.add_reaction(e)




    async def main_mono(user):        
        # en attente d'une action
        await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", "en attente...", "..."))
        
        # si le joueur est en prison et qu'il peut utiliser une carte sortie, lui propose de l'utiliser
        if user.prison_ != 0 and user.sorti_prison:
            await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"...", f"**{user.name}**, voulez-vous utilisez votre carte sorti de prison ?"))

            try:
                num, _ = await client.wait_for("reaction_add", check=lambda reaction, user_: user_.id == user.id and str(reaction.emoji) in ["✅", "❌"], timeout=300)
            except asyncio.TimeoutError:
                pass
            else:
                if str(num.emoji) == "✅":
                    user.sorti_prison = False
                    await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"...", f"Vous avez utilisez votre carte !"))
                else:
                    await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"...", f"Vous n'avez pas utilisez votre carte !"))

                await asyncio.sleep(3)
                await msg.clear_reactions()
                for e in ["🎲", "ℹ️"]:
                    await msg.add_reaction(e)


        # si le joueur n'est pas en prison le tour se passe normalement
        if user.prison_ == 0:

            # attends que le joueur utilise une reaction
            try:
                num, user_emote = await client.wait_for("reaction_add", check=lambda reaction, user_: user_.id == user.id and str(reaction.emoji) in ["🎲", "ℹ️", "🛑"], timeout=300)
            except asyncio.TimeoutError:
                # si le joueur est afk on passe son tour
                await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", f"", f"{user.name} n'a pas jouer on saute son tour"))
                await asyncio.sleep(3)
                return False

            await msg.remove_reaction(num.emoji, user_emote)

            

            # si le joueur réagit avec le dé le fonction
            if str(num.emoji) == "🎲":
                await joue(user)
            elif str(num.emoji) == "ℹ️":
                # si il a appuyer sur la reaction info
                # envoie la liste de ses proprietes
                text_propri = "".join(f"{terrain.emote}: {terrain.nom}, {terrain.valeur}\n" for terrain in user.proprietes)
                if text_propri == "":
                    text_propri = "Vous possedez aucune propriete"

                embed=discord.Embed()
                embed.add_field(name=f"Argent", value=f"{user.argent} ₿" , inline=False)
                embed.add_field(name=f"Proprietes de {user.name}, total: {len(user.proprietes)}", value=text_propri , inline=False)
                info = await ctx.send(embed=embed)

                # attends que le joueur appuye sur la croix pour fermer le panel d'information
                try:
                    await info.add_reaction("❌")
                except:
                    await msg.clear_reactions()
                    await info.add_reaction("❌")
                try:
                    num, user_emote = await client.wait_for("reaction_add", check=lambda reaction, user_: user_.id == user.id and str(reaction.emoji) == "❌", timeout=300)
                except asyncio.TimeoutError:
                    pass

                
                # supprime le message d'information et relance le tour 
                await info.delete()
                await main_mono(user)
            elif str(num.emoji) == "🛑":
                await msg.edit(embed=discord_embed("...", "...", "partie annulée"))
                return True


            
        else:
            user.prison_ -= 1

        return False

    while True:
        for user in liste_joueurs:
            
            # véréfication de la victoire
            if len(liste_joueurs) == 1:
                await msg.edit(embed=discord_embed(f"{user.mention}, ₿: {user.argent}", "...", f"Partie terminée le gagnant est {user.mention}"))
                return 

            if await main_mono(user):
                return
            await asyncio.sleep(4)





            

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
"""
@puissance4.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque le membre a affronter ! syntaxe: {prefix}puissance4 <membre>")
"""

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
async def dm(ctx, member, *, msg):
    member = get_member(member)
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
    member = get_member(member)
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
            if message.jump_url == arg:
                await ctx.send(f"{tmp - 2} messages sélectionné jusqu'au message demandé. voulez-vous les supprimer ? (oui/non)")
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
    if ctx.author.id != 236853417681616906:
        return
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
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{message.author.name} à supprimé un message", icon_url=message.author.avatar_url)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/836943322580516904/914539782040850472/unknown.png")
        if message.content == "":
            embed.add_field(name="contenu", value="<image>", inline=True)
        else:
            embed.add_field(name="contenu", value=message.content, inline=True)
        embed.add_field(name=f"󠀮salon", value=message.channel.mention, inline=True)
        embed.add_field(name="󠀮 ", value=message.author.mention + " - " + get_time(), inline=False)
        msg = await channel_send(dico[message.guild.id]["logs"]).send(embed=embed)
        
        if len(message.attachments) != 0:
            files = []
            for attachment in message.attachments:
                await attachment.save(attachment.filename)
                files.append(attachment.filename)

            for index, file in enumerate(files):
                embed=discord.Embed(color=0xf0a3ff)
                embed.set_author(name=f"{message.author.name} à supprimé un message", icon_url=message.author.avatar_url)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/836943322580516904/914539782040850472/unknown.png")
                    
                if file.endswith(".mp4"):
                    embed.video.url = f"attachment://{file}"
                    embed.video.height = message.attachments[index]
                    embed.video.width = message.attachments[index]
                else:
                    embed.set_image(url=f"attachment://{file}")
                    
                embed.add_field(name=f"󠀮salon", value=message.channel.mention, inline=True)
                embed.add_field(name="󠀮 ", value=message.author.mention + " - " + get_time(), inline=False)
                ds_file = discord.File(file)
                await msg.reply(file=ds_file, embed=embed)
                os.remove(file)

@client.event
async def on_message_edit(before, after):
    if before.author.bot or before.guild is None or before.content == after.content:
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
client.run(os.environ["token"])