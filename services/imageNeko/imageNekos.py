import requests

from discord.ext import commands


class ImageNekos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = "http://api.nekos.fun:8080/api/"

        self.error_msg = ""

        self.sfw_tags = [
            "kiss",
            "lick",
            "hug",
            "baka",
            "cry",
            "poke",
            "smug",
            "slap",
            "tickle",
            "pat",
            "laugh",
            "feed",
            "cuddle",
        ]

    def get_image(self, tag: str) -> str:
        if tag not in self.sfw_tags:
            return f"Le tag {tag} n'existe pas.\nListe de tags disponibles\n{self.error_msg}"

        # récupère le lien d'une image aléatoire
        res = requests.get(self.url + tag)

        return res.json()["image"]
