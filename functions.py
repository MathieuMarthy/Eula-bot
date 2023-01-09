import json
import os
import asyncio
import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands
from discord.ext import commands

project_path = os.path.dirname(os.path.realpath(__file__))

def is_me(ctx: commands.Context) -> bool:
    return ctx.author.id == 236853417681616906


class Utils:
    def __init__(self, client: discord.Client):
        self.client = client
        self.server_config = json.load(open(os.path.join(project_path, "data", "server_config.json"), "r", encoding="utf-8"))


    def server_exists_in_config(self, guild_id: int) -> bool:
        return str(guild_id) in self.server_config


    def add_new_server(self, guild_id: int):
        self.server_config[str(guild_id)] = {
            "welcome_message": {
                "active": False,
                "message": ""
            },
            "logs": {
                "active": False,
                "channel_id": 0
            },
            "autorole": {
                "active": False,
                "role_id": 0
            },
            "rolevocal": {
                "active": False,
                "role_id": 0
            }
        }
        self._save_server_config()


    def get_server_config(self, guild_id: int, *keys: str):
        if len(keys) == 0:
            return self.server_config[str(guild_id)]
        else:
            config = self.server_config[str(guild_id)]
            for arg in keys:
                config = config[arg]
            return config
    
    
    def _save_server_config(self):
        json.dump(self.server_config, open(os.path.join(self.bot_path(), "data", "server_config.json"), "w", encoding="utf-8"), indent=4)

    
    def set_server_config(self, guild_id: int, *keys: str, value):
        config = self.server_config[str(guild_id)]
        for key in keys[:-1]:
            config = config[key]
        config[keys[-1]] = value
        self._save_server_config()


    def bot_path(self) -> str:
        return project_path


    def channel_send(self, id):
        return self.client.get_channel(id)


    def replaces(self, string, *args):
        for i in range(0, len(args), 2):
            string = string.replace(args[i], args[i + 1])
        return string
    

    async def is_member(self, member: str, guild: discord.Guild) -> bool:

        for char in ["<", "@", "!", ">"]:
            member = member.replace(char, "")
        
        if not member.isdigit() and len(member) != 18:
            return False

        member = await guild.fetch_member(member)
        return member is not None
 

    async def is_user(self, member: str) -> bool:

        for char in ["<", "@", "!", ">"]:
            member = member.replace(char, "")

        if not member.isdigit() and len(member) != 18:
            return False

        member = await self.client.fetch_user(member)
        return member is not None


    def get_date_time(self):
        return datetime.now(tz=ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y %H:%M:%S")


    def embed_color(self):
        return 0x989eec


    def error_message(self, error: discord.DiscordException) -> str:
        if isinstance(error, commands.MissingRequiredArgument):
            return "Il manque un ou plusieurs arguments\nutilisez `/help` pour plus d'informations"
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, app_commands.errors.MissingPermissions):
            return "Vous n'avez pas les permissions d'utiliser cette commande"
        elif isinstance(error, commands.BotMissingPermissions) or isinstance(error, app_commands.errors.BotMissingPermissions):
            return "Le bot n'a pas les permissions d'utiliser cette commande"
        else:
            return None
        

    async def start_game_multi(self, ctx, limit, name_game):
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
                            if user.id != self.client.user.id:
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


    async def start_game_duo(self, ctx: commands.Context, member, name_game):
        member = ctx.guild.get_member(member)

        if member is None:
            await ctx.send("Vous n'avez pas mentionné un joueur")
            return False, None

        await ctx.send(f"{member.mention} acceptez-vous la partie de {name_game} contre **{ctx.author.name}** ?")
        try:
            msg = await self.client.wait_for("message", check=lambda message: message.author.id in [member.id,
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
        
    async def end_game(self, ctx, list_user, dico_points):
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
            username = self.client.get_user(list_winner[0])
            await ctx.send(
                f"󠀮 \n**Partie finie !**\nLe vainqueur est {username.mention} avec {dico_points[username.id]} points !")
        else:
            str_winner = ""
            for e in list_winner:
                username = self.client.get_user(e)
                str_winner += " " + username.mention
            await ctx.send(
                f"󠀮 \n**Partie finie !**\nLes vainqueurs sont {str_winner} avec {dico_points[username.id]} points !")


    def get_img(self, name: str) -> str:
        """
        power
        shuffle
        plus
        minus
        notif
        edit
        plus_rond
        croix_non
        croix_plus
        speaker
        trash
        setting
        speaker_x
        mic
        exit
        enter
        setting_bar
        face
        pile
        """
        return dico[name]


dico = {
    "power": "https://media.discordapp.net/attachments/836943322580516904/971846167078006814/unknown.png",
    "shuffle": "https://media.discordapp.net/attachments/836943322580516904/971846499443019776/unknown.png",
    "plus": "https://media.discordapp.net/attachments/836943322580516904/971846604321599548/unknown.png",
    "minus": "https://media.discordapp.net/attachments/836943322580516904/971847114445443112/unknown.png",
    "notif": "https://media.discordapp.net/attachments/836943322580516904/971847177741684826/unknown.png",
    "edit": "https://media.discordapp.net/attachments/836943322580516904/971847238395498646/unknown.png",
    "plus_rond": "https://media.discordapp.net/attachments/836943322580516904/971847381379350578/unknown.png",
    "croix_non": "https://media.discordapp.net/attachments/836943322580516904/971847400287268924/unknown.png",
    "croix_plus": "https://media.discordapp.net/attachments/836943322580516904/971847415143485460/unknown.png",
    "speaker": "https://media.discordapp.net/attachments/836943322580516904/971847435041247385/unknown.png",
    "trash": "https://media.discordapp.net/attachments/836943322580516904/971847444780425266/unknown.png",
    "setting": "https://media.discordapp.net/attachments/836943322580516904/971847454892908614/unknown.png",
    "speaker_x": "https://media.discordapp.net/attachments/836943322580516904/971847489453961296/unknown.png",
    "mic": "https://media.discordapp.net/attachments/836943322580516904/971847505920786492/unknown.png",
    "exit": "https://media.discordapp.net/attachments/836943322580516904/971847553664548934/unknown.png",
    "enter": "https://media.discordapp.net/attachments/836943322580516904/971847616151298078/unknown.png",
    "setting_bar": "https://media.discordapp.net/attachments/836943322580516904/971847628667097198/unknown.png",
    "face": "https://media.discordapp.net/attachments/836943322580516904/971841674156339370/face_eula.png",
    "pile": "https://media.discordapp.net/attachments/836943322580516904/971843297117077584/pile_eula.png",
}