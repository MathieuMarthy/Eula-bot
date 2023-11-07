import discord
from discord.ui import View

from functions import Utils
from data import config


help_dict = {
    "🏠 Accueil": {
        "commandes": {
            "Aide": "Si vous avez des propositions ou si vous avez trouvez des bugs contactez moi kojhyy#0012",
            "Naviguer" : "Vous pouvez naviguez dans les catégories avec la liste déroulante",
        },
        "image": "https://media.discordapp.net/attachments/836943322580516904/1060614756458840134/1159087.png"
    },
    "👑 Admin": {
        "commandes": {
            "send": "Envoie un message dans un salon",
            "send_embed": "Envoie un embed dans un salon",
            "help_send_embed": "envoi un message d'aide pour la commande send_embed",
            "clear": "Supprime un nombre de messages, ou jusqu'à un message donné",
            "nuke": "supprimer un salon et le recréer avec les mêmes paramètres",
            "reaction": "Mets des réactions sur un message",
            "timeout": "timeout une personne pendant une durée",
            "sondage": "Crée un sondage avec jusqu'à 5 choix",
            "toggle_autorole": "active ou désactive l'assignation d'un rôle quand on rentre dans le serveur",
            "toggle_logs": "active ou désactive les logs",
            "toggles_logs": "active ou désactive l'assignation d'un rôle quand un utilisateur rejoint un salon vocal",
            "toggle_welcome_message": "active ou désactive le message de bienvenue en DM"
        },
        "image": "https://media.discordapp.net/attachments/836943322580516904/1060984169779449916/maxresdefault.png"
    },
    "💬 Chat": {
        "commandes": {
            "bonjour": "dit bonjour à quelqu'un !",
            "mord": "mords quelqu'un !",
            "bisous": "fait un bisous à quelqu'un !",
            "tapoter": "*pat pat*",
            "calin": "🤗",
            "baka": "ba...baka !",
        },
        "image": "https://media.discordapp.net/attachments/836943322580516904/1060985289448894565/image.png"
    },
    "🔧 Utilitaire": {
        "commandes": {
            "pp": "envoie la pp d'une personne",
            "bannière": "envoie la bannière d'une personne",
            "ping": "ping le bot",
            "choisis": "choisis entre plusieurs propositions (séparées par des virgules)",
        },
        "image": "https://media.discordapp.net/attachments/836943322580516904/1060986942377959484/image.png"
    },
    "🌍 General": {
        "commandes": {
            "reddit": "envoie des images d'un subreddit",
            "8ball": "la boule magique répond à vos questions",
            "pile_ou_face": "pile_ou_face",
            "randomizer_lol": "donne un champion, stuff et runes aléatoire",
            "image_sfw": "envoie une image d'animé aléatoire",
            "image_nsfw": "envoie une d'animé image nsfw aléatoire"
        },
        "image": "https://media.discordapp.net/attachments/836943322580516904/1060991182748008600/E09Nv5fWEAIeiy2.png"
    },
    "🎮 Jeux": {
        "commandes": {
            "10fastfingers": "multijoueur: dans ce jeu, vous devez taper le plus de mots possible",
            "monopoly": "multijoueur : jeu de monopoly avec des règles personnalisées, objets, ...",
        },
        "image": "https://media.discordapp.net/attachments/836943322580516904/1063440044364402698/5ech2agzst1a1.png"
    }
}

class HelpView(View):
    def __init__(self, client):
        super().__init__(timeout=300)
        self.utils = Utils.get_instance(client)

        self.embed = discord.Embed(title="Menu d'aide", color=self.utils.embed_color())
        self.embed.set_author(name=client.user.display_name, icon_url=client.user.avatar.url)


    @discord.ui.select(
        placeholder=list(help_dict.keys())[0],
        options = [
            discord.SelectOption(label=key, value=key)
                for key in help_dict.keys()
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        embed = await self.embed_from_category(select.values[0])

        view = View()
        select.placeholder = select.values[0]
        view.add_item(select)
        await interaction.response.edit_message(embed=embed, view=view)


    async def embed_from_category(self, category: str) -> discord.Embed:
        category = help_dict[category]

        category_embed = self.embed.copy()
        category_embed.set_image(url=category["image"])
        for name, description in category["commandes"].items():
            category_embed.add_field(name=name, value=description, inline=False)
        
        category_embed.set_footer(text=f"version: {config.version}")
        return category_embed

    
    async def default_embed(self) -> discord.Embed:
        return await self.embed_from_category(list(help_dict.keys())[0])
