import discord
import datetime
from zoneinfo import ZoneInfo

class Utils:
    def __init__(self, client: discord.Client):
        self.client = client
    
    def channel_send(self, id):
        return self.client.get_channel(id)


    def get_date_time(self):
        return datetime.now(tz=ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y %H:%M:%S")

    def get_img(name: str) -> str:
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