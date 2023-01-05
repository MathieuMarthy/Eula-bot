import datetime
import os
from zoneinfo import ZoneInfo

import discord

class Utils:
    def __init__(self, client: discord.Client):
        self.client = client
    
    def bot_path(self) -> str:
        return os.path.dirname(os.path.realpath(__file__))

    def channel_send(self, id):
        return self.client.get_channel(id)
        
    
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