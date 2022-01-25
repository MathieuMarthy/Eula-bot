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
# forme:  {id: {"name": str, "logs": bool, "logs_id": int, "voc": int}}



# --- setup
prefix = "!"
decalage_horaire = 1
default_intents = discord.Intents.default()
default_intents.members = True
client = commands.Bot(command_prefix = prefix, help_command = None, intents = default_intents)

print("connection...", end = "")


@client.event
async def on_ready():
    print("\rconnecté ! ⊂(◉‿◉)つ")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"{prefix}help"))
    for serveur in client.guilds:
        if serveur.id not in dico:
           dico[serveur.id] =  {"name": serveur.name, "logs": None, "voc": None, "autorole": None}
    open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))

# --- fonctions
def channel_send(id):
    return client.get_channel(id)

def get_time():
    time_ = str(time.strftime("%d/%m/%Y - %H:%M:%S", time.localtime()))
    hour = time.strftime("%H", time.localtime())
    return time_.replace(hour, str(int(hour) + decalage_horaire))



@client.event
async def on_message(message):
    if message.content.endswith("quoi ?"):
        await message.channel.send("feur")

    await client.process_commands(message)


# --- commands
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
        
    if not ctx.channel.is_nsfw():
        await ctx.send("Il faut que le salon soit nsfw pour que la commande fonctionne")
        return

    if category in ["ass","bdsm","cum","creampie","manga","femdom","hentai","incest","masturbation","public","ero","orgy","elves","yuri","pantsu","glasses","cuckold","blowjob","boobjob","foot","thighs","vagina","ahegao","uniform","gangbang","tentacles","gif","neko","nsfwMobileWallpaper","zettaiRyouiki"]:
        for _ in range(nbr):
            response = requests.get(f"https://hmtai.herokuapp.com/nsfw/{category}")
            link = ast.literal_eval(response.text)
            await ctx.send(link["url"])
    else:
        await ctx.send("**Liste des categories:**\nass, bdsm, cum, creampie, manga, femdom, hentai, incest, masturbation, public, ero, orgy, elves, yuri, pantsu, glasses, cuckold, blowjob, boobjob, foot, thighs, vagina, ahegao, uniform, gangbang, tentacles, gif, neko, nsfwMobileWallpaper, zettaiRyouiki")


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
async def eightball(ctx):
    a = ["Une chance sur deux", "D'après moi oui", "C'est certain", "Oui absolument", "Sans aucun doute", "Très probable", "Oui", "C'est bien parti", "C'est non", "Peu probable", "Faut pas rêver", "N'y compte pas", "Impossible"]
    if ctx.message.content.lower() == "!8 ratio ?":
        await ctx.send("ratio")
    else:
        await ctx.send(a[random.randint(0, len(a) - 1)])


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
        embed.add_field(name=f"\n{prefix}enable_logs - _admin_", value="active les logs", inline=False)
        embed.add_field(name=f"{prefix}disable_logs - _admin_", value="désactive les logs", inline=False)
        embed.add_field(name=f"{prefix}clear <nbr/texte> - _admin_", value="supprime le nombres de messages,\nsupprime les messages jusqu'au texte donné", inline=False)
        embed.add_field(name=f"{prefix}nuck <salon> - _admin_", value="enleve tous les messages d'un salon", inline=False)
        embed.add_field(name=f"{prefix}role_vocal_on <role> - _admin_", value="donne un role à chaque fois qu'un membre rejoint un salon vocal ", inline=False)
        embed.add_field(name=f"{prefix}role_vocal_off - _admin_", value="desactive la commande role_vocal_on", inline=False)
        embed.add_field(name=f"{prefix}auto_role_on <role> - _admin_", value="donne un role à tous les nouveaux arrivant", inline=False)
        embed.add_field(name=f"{prefix}auto_role_off - _admin_", value="désactive l'auto_role", inline=False)
        embed.add_field(name=f"{prefix}say <salon> <message> - _admin_", value="envoie un message dans un salon", inline=False)
        embed.add_field(name=f"{prefix}reaction <salon> <id du msg> <reactions>", value="le bot réagit au message avec les reactions donnés, les reaction doivent être coller", inline=False)
    embed.add_field(name=f"{prefix}8ball", value="Boule magique", inline=False)
    embed.add_field(name=f"{prefix}random", value="donne un nombre aleatoire entre 0 et le nombre donné", inline=False)
    embed.add_field(name=f"{prefix}ping", value="ping le bot", inline=False)
    embed.add_field(name=f"{prefix}hentai <categorie> <nbr d'images>", value="si le salon est NSFW envoie des images hentai", inline=False)
    await ctx.send(embed=embed)
    # embed.add_field(name=f"{prefix}", value="", inline=False)


# - jeu
@client.command(aliases=["10fastfinger", "10ff"])
async def jeu_reaction(ctx):
    msg = await ctx.send("**Partie de 10fastfinger lancée !**\npour participer réagissez avec 🖐️")
    await msg.add_reaction("🖐️")
    time.sleep(15)
    list_user = []
    async for e in ctx.channel.history(limit=100):
        if e.id == msg.id:
            for reaction in e.reactions:
                if reaction.emoji == "🖐️":
                    async for user in reaction.users():
                        if user.id != client.user.id:
                            list_user.append(user)
            break

    str_name = ""
    dico_points = {}
    for i in list_user:
        dico_points[i.id] = 0
        str_name += ", " + i.name
    str_name = str_name.replace(", ", "", 1)
    await ctx.send(f"Liste des participants: {str_name}\nC'est parti pour 5 manches !")
    time.sleep(3)

    turn = 0
    list_question = ["Bonjour je m'appelle Nicolas", "Salut ! ça va ?", "Eula c'est vraiment la meilleure waifu de Genshin Impact", "Je mange des carottes", "Un sourd-muet séparera cinq catastrophes et un tendon"]
    while turn != 5:
        mot = list_question[random.randint(0, len(list_question) - 1)]
        await ctx.send(f"`{mot}`")
        list_question.remove(mot)
        try:
            msg = await client.wait_for("message", check=lambda message: message.author in list_user and message.content == mot, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("partie fini à cause d'inactivité")
        dico_points[msg.author.id] += 1
        await ctx.send(f"**{msg.author}** gagne le point ! {dico_points[msg.author.id]} points")
        turn += 1
        time.sleep(3)

    n = (list_user[0].id, dico_points[list_user[0].id])
    for id, point in dico_points.items():
        if n[1] < point:
            n = (id, point)
    list_winner = [id for id, point in dico_points.items() if n[1] == point]
    if len(list_winner) == 1:
        username = client.get_user(list_winner[0])
        await ctx.send(f"󠀮 \n**Partie fini !**\nLe vainqueur est {username.mention} avec {dico_points[username.id]} points !")
    else:
        str_winner = ""
        for i, e in enumerate(list_winner):
            username = client.get_user(list_winner[i])
            str_winner += " " + username.mention
        await ctx.send(f"󠀮 \n**Partie fini !**\nLes vainqueurs sont {str_winner} avec {dico_points[username.id]} points !")

            

# - admin
@client.command()
@has_permissions(administrator=True)
async def reaction(ctx, channel, id, *, react):
    if not channel.isdigit():
        channel = channel.replace("<", "").replace("#", "").replace(">", "")

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


@client.command()
@has_permissions(administrator=True)
async def say(ctx, channel, *, message):
    if not channel.isdigit():
        channel = channel.replace("<", "").replace("#", "").replace(">", "")

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
async def auto_role_on(ctx, role: discord.Role):
    dico[ctx.guild.id]["autorole"] = role.id
    open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
    await ctx.send(f"Le role {role.mention} est maintenant donné à tous les nouveaux arrivant !")

@client.command()
@has_permissions(administrator=True)
async def auto_role_off(ctx):
    dico[ctx.guild.id]["autorole"] = None
    open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
    await ctx.send("La fonction d'autorole est maintenant désactiver")

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
                if msg.content in ["oui", "o", "y", "yes"]:
                    await ctx.channel.purge(limit = tmp + 1)
                else:
                    await msg.add_reaction("✅")
                return


@client.command()
@has_permissions(administrator=True)
async def nuck(ctx, channel):
    if not channel.isdigit():
        channel = channel.replace("<", "").replace("#", "").replace(">", "")

    channel = client.get_channel(int(channel))
    if channel is None:
        await ctx.send("salon non trouvé")
        return
    
    await ctx.send(f"Voulez-vous vraiment nuck le salon {channel.mention} ?")
    try:
        reponse = await client.wait_for("message", check = lambda message: message.author.id == ctx.author.id, timeout = 30)
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
async def role_vocal_on(ctx, role: discord.Role):
    await ctx.send(f"Le role {role.mention} est maintenant donné à toutes les personnes qui rentre dans un salon vocal !")
    dico[ctx.author.guild.id]["voc"] = role.id
    open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))

@role_vocal_on.error
async def on_message_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Il manque le role ! syntaxe: {prefix}role_vocal_on <role>")


@client.command()
@has_permissions(administrator=True)
async def role_vocal_off(ctx):
    await ctx.send("Plus aucun role ne sera donner quand quelqu'un rejoint un salon vocal")
    dico[ctx.author.guild.id]["voc"] = None
    open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))


@client.command()
@has_permissions(administrator=True)
async def enable_logs(ctx, salon):
    if dico[ctx.guild.id]["logs"] is not None:
        await ctx.send("Les logs sont déjà activé")
    else:
        await ctx.send("dans quel salon ?")
        try:
            reponse = await client.wait_for("message", check = lambda message: message.author.id == ctx.author.id, timeout = 30)
            while not reponse.content.replace("<", "").replace(">", "").replace("#", "").isdigit():
                reponse = await client.wait_for("message", check = lambda message: message.author.id == ctx.author.id, timeout = 30)
        except asyncio.TimeoutError:
            await ctx.send("délai dépassé")
            return
        channel_id = reponse.content.replace("<", "").replace(">", "").replace("#", "")
        channel = client.get_channel(int(channel_id))
        await ctx.send(f"Le salon est bien {channel.mention} ? (oui/non)")
        try:
            reponse = await client.wait_for("message", check = lambda message: message.author.id == ctx.author.id, timeout = 30)
        except asyncio.TimeoutError:
            await ctx.send("délai dépassé")
            return
        if reponse.content.lower() in ["yes", "y", "o", "oui"]:
            dico[ctx.guild.id]["logs"] = channel.id
            open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))
            await ctx.send(f"Les logs sont maintenant activés dans {channel.mention} !")


@client.command()
@has_permissions(administrator=True)
async def disable_logs(ctx):
    dico[ctx.guild.id]["logs"] = None
    await ctx.send("Les logs sont maintenant désactivé !")
    open("/home/runner/Eula-bot/server.txt", "w").write(str(dico))


@client.command()
async def view(ctx):
    reponse = await client.wait_for("message", check = lambda message: message.author.id == ctx.author.id, timeout = 30)
    print(reponse.content)


# --- logs
# - message
@client.event
async def on_message_delete(message):
    if message.author.bot:
        return
    if dico[message.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{message.author.name} à supprimer un message", icon_url=message.author.avatar_url)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/836943322580516904/914539782040850472/unknown.png")
        embed.add_field(name="contenu", value=message.content, inline=True)
        embed.add_field(name=f"󠀮salon", value=message.channel.mention, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[message.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    elif before.content.startswith("http") and before.content.count(" ") == 0 and before.content == after.content:
        return
    if dico[before.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{before.author.name} à modifier un message", icon_url=before.author.avatar_url)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914861144206893076/edit.png")
        embed.add_field(name="avant", value=before.content, inline=True)
        embed.add_field(name="󠀮salon", value=before.channel.mention, inline=True)
        embed.add_field(name="après", value=after.content, inline=False)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


# - channel
@client.event
async def on_guild_channel_create(channel):
    if dico[channel.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"channel créé", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914918043170259074/plus_1.png")
        embed.add_field(name=f"󠀮salon", value=channel.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[channel.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_guild_channel_delete(channel):
    if dico[channel.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"channel supprimer", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
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
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)


# - role
@client.event
async def on_guild_role_create(role):
    if dico[role.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"un nouveau role à été créé", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914918043170259074/plus_1.png")
        embed.add_field(name="nom", value=role.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
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
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
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
        embed.add_field(name="membre", value=member.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[guild.id]["logs"]).send(embed=embed)


@client.event
async def on_member_unban(guild, member):
    if dico[guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} à été débanni", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914883218275205160/notifications.png")
        embed.add_field(name="membre", value=member.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[guild.id]["logs"]).send(embed=embed)


@client.event
async def on_member_join(member):
    if dico[member.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} à rejoint le serveur", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914883218275205160/notifications.png")
        embed.add_field(name="membre", value=member.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)
    if dico[member.guild.id]["autorole"] is not None and not member.bot:
        role = discord.utils.get(member.guild.roles, id = dico[member.guild.id]["autorole"])
        await member.add_roles(role)

        
@client.event
async def on_member_remove(member):
    if dico[member.guild.id]["logs"] is not None:
        embed=discord.Embed(color=0xf0a3ff)
        embed.set_author(name=f"{member.name} à quitté le serveur", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914883218275205160/notifications.png")
        embed.add_field(name="membre", value=member.name, inline=True)
        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
        await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)


@client.event
async def on_member_update(before, after):
    if dico[before.guild.id]["logs"] is not None:
        if before.name != after.name:
            embed=discord.Embed(color=0xf0a3ff)
            embed.set_author(name=f"{before.name} à changé de surnom", icon_url="https://media.discordapp.net/attachments/836943322580516904/914539780363145336/unknown.png")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914861144206893076/edit.png")
            embed.add_field(name="avant", value=before.name, inline=True)
            embed.add_field(name="après", value=after.name, inline=True)
            embed.add_field(name="󠀮 ", value=get_time(), inline=False)
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
                        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
                        await channel_send(dico[before.guild.id]["logs"]).send(embed=embed)
            else:
                i = diff(before.roles, after.roles)
                for e in i:
                    if before.roles[e].id != dico[before.guild.id]["voc"]:
                        embed=discord.Embed(color=0xf0a3ff)
                        embed.set_author(name=f"{before.name} à perdu un role", icon_url=before.avatar_url)
                        embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914918042981498910/minus.png")
                        embed.add_field(name="role", value=before.roles[e].mention, inline=True)
                        embed.add_field(name="󠀮 ", value=get_time(), inline=False)
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
                embed.add_field(name="󠀮 ", value=get_time(), inline=False)
                await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)
                if dico[member.guild.id]["voc"] is not None:
                    await member.add_roles(discord.utils.get(member.guild.roles, id = dico[member.guild.id]["voc"]))
            elif after.channel is None:
                embed=discord.Embed(color=0xf0a3ff)
                embed.set_author(name=f"{member.name} à quitté un salon vocal", icon_url=member.avatar_url)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914539761794961458/unknown.png")
                embed.add_field(name=f"󠀮salon", value=before.channel.mention, inline=True)
                embed.add_field(name="󠀮 ", value=get_time(), inline=False)
                await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)
                if dico[member.guild.id]["voc"] is not None:
                    await member.remove_roles(discord.utils.get(member.guild.roles, id = dico[member.guild.id]["voc"]))
            else:
                embed=discord.Embed(color=0xf0a3ff)
                embed.set_author(name=f"{member.name} à changer de salon vocal", icon_url=member.avatar_url)
                embed.set_thumbnail(url="https://media.discordapp.net/attachments/836943322580516904/914922944000577536/shuffle.png")
                embed.add_field(name=f"󠀮avant", value=before.channel.mention, inline=True)
                embed.add_field(name=f"󠀮après", value=after.channel.mention, inline=True)
                embed.add_field(name="󠀮 ", value=get_time(), inline=False)
                await channel_send(dico[member.guild.id]["logs"]).send(embed=embed)


keep_alive()
client.run(os.environ['token'])