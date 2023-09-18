import os
import random

from PIL import Image
import discord
from discord import app_commands
from discord.ui import Button, View
from discord.ext import commands

from assets.League_of_legends import data_lol
from functions import Utils

class Randomizer(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)
        self.secret_channel = 1023522913825071195
        self.assets_path = os.path.join(self.utils.bot_path(), "assets/League_of_legends/images")
        self.dict_lanes = {
            1: "Toplane",
            2: "Jungle",
            3: "Midlane",
            4: "Botlane",
            5: "Support",
        }

    async def send_image(self, lane, champion) -> discord.Embed:
        embed = discord.Embed(title=f"Randomizer{f' - {self.dict_lanes[lane]}' if lane is not None else ''}{f' - {champion}' if champion is not None else ''}", color=self.utils.embed_color())

        # création de l'image
        image_path = self.randomizer_image(lane, champion)

        # envoi de l'image
        with open(image_path, "rb") as f:
            image = discord.File(f)
            msg: discord.Message = await self.client.get_channel(self.secret_channel).send(file=image)

        image_url = msg.attachments[0].url
        embed.set_image(url=image_url)
        return embed

    async def command(self, ctx: commands.Context, lane, champion):

        # discord ui
        view = View()
        button = Button(style=discord.ButtonStyle.blurple, emoji="🔄")
        view.add_item(button)

        # callback fonction / actualisation de l'image
        async def callback_button_refresh(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("Vous n'avez pas le droit de relancer pour les autres", ephemeral=True)
                return

            embed = await self.send_image(lane, champion)
            await interaction.response.edit_message(embed=embed)

        button.callback = callback_button_refresh

        embed = await self.send_image(lane, champion)
        await ctx.reply(embed=embed, view=view, mention_author=False)


    @commands.command()
    async def randomizerlol(self, ctx, option=None):
        lane = None
        champion = None
        if option is not None:
            for string in option.split(" "):
                if string.isdigit() and (int(string) < 0 and int(string) <= 5):
                    lane = string
                else:
                    champion = string

        await self.command(ctx, lane, champion)


    @app_commands.command(name="randomizer_lol", description="donne un champion, stuff et runes aléatoire")
    @app_commands.describe(lane="forcé le choix d'une lane")
    @app_commands.describe(champion="forcé le choix d'un champion")
    @app_commands.choices(
        lane=[
            app_commands.Choice(name="Toplane", value=1),
            app_commands.Choice(name="Jungle", value=2),
            app_commands.Choice(name="Midlane", value=3),
            app_commands.Choice(name="Botlane", value=4),
            app_commands.Choice(name="Support", value=5),
        ]
    )
    async def randomizerlolSlash(self, interaction: discord.Interaction, lane: int=None, champion: str=None):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, lane, champion)


    def runes(self) -> list[str]:
        """Retourne la liste des chemins des images de runes random"""
        assets_runes_path = self.assets_path + "/runes"
        branches = os.listdir(assets_runes_path)

        # choisi une branche principal aléatoirement
        path_list_of_runes = []
        path_main_branch = assets_runes_path + "/" + random.choice(branches)
        path_list_of_runes.append(
            path_main_branch + "/principal/" + random.choice(os.listdir(path_main_branch + "/principal")))

        # choisi les petites runes de la branche principale
        for i in range(1, 4):
            path_list_of_runes.append(path_main_branch + f"/secondaire/{i}/" + random.choice(
                os.listdir(path_main_branch + "/secondaire" + f"/{i}")))

        # choisi les runes secondaires
        path_secondary_branch = assets_runes_path + "/" + random.choice(branches)
        while path_secondary_branch == path_main_branch:
            path_secondary_branch = assets_runes_path + "/" + random.choice(branches)

        tmp = [1, 2, 3]
        secondary_branches = [tmp.pop(tmp.index(random.choice(tmp))) for _ in range(2)]
        for secondary_branch in secondary_branches:
            path_list_of_runes.append(path_secondary_branch + f"/secondaire/{secondary_branch}/" + random.choice(
                os.listdir(path_secondary_branch + f"/secondaire/{secondary_branch}/")))

        # choisi les runes bonus
        for i in range(1, 4):
            path_list_of_runes.append(
                self.assets_path + f"/runes_shards/{i}/" + random.choice(os.listdir(self.assets_path + f"/runes_shards/{i}")))

        return path_list_of_runes


    def champion(self) -> str:
        return f"{self.assets_path}/champions/" + random.choice(os.listdir(f"{self.assets_path}/champions"))


    def lane(self):
        """
        1 -> top
        2 -> jungle
        3 -> mid
        4 -> adc
        5 -> support
        """
        return random.randint(1, 5)


    def summoners(self, jungle: bool = False) -> list[str]:
        assets_summoners_path = self.assets_path + "/summoners"
        random_summoners = []
        list_of_summoners = os.listdir(assets_summoners_path)
        list_of_summoners.remove("smite.png")

        # si le joueur est un jungle il lui faut un smite
        if jungle:
            random_summoners.append(assets_summoners_path + "/smite.png")

        # ajout des summoner aléatoirement
        while len(random_summoners) != 2:
            random_summoner = random.choice(list_of_summoners)

            # si le sort aléatoire n'est pas déjà dans la liste on l'ajoute
            if assets_summoners_path + "/" + random_summoner not in random_summoners:
                random_summoners.append(assets_summoners_path + "/" + random_summoner)

        return random_summoners


    def build(self, lane, champion) -> dict:
        dico = {"champion": self.champion(), "lane": self.lane(), "runes": self.runes(), "items": [], "summoners": [], "starter": ""}

        if lane in [1, 2, 3, 4, 5]:
            dico["lane"] = lane

        if champion is not None:
            champion =  champion.replace("'", "").replace("-", "").replace(".", "").replace(" ", "").lower() + ".png"
            liste = data_lol.melee_champion + data_lol.range_champion
            if champion in liste:
                dico["champion"] = f"{self.assets_path}/champions/{champion}"

        dico["summoners"] = self.summoners(dico["lane"] == 2)

        # starter jungler
        if dico["lane"] == 2:
            dico["starter"] = self.assets_path + "/smite/" + random.choice(os.listdir(self.assets_path + "/smite"))

        # starter support
        elif dico["lane"] == 5:
            item_support = random.randint(1, 4)
            dico["starter"] = self.assets_path + f"/support/{item_support}/start.png"
            dico["items"].append(self.assets_path + f"/support/{item_support}/final.png")

        # starter
        else:
            dico["starter"] = self.assets_path + f"/starter/" + random.choice(os.listdir(self.assets_path + f"/starter"))

        # bottes aléatoire
        if dico["champion"].split("/")[-1] != "cassiopeia.png":
            dico["items"].append(self.assets_path + "/items/Boots/" + random.choice(os.listdir(self.assets_path + "/items/Boots")))

        # mythique aléatoire
        dico["items"].append(self.assets_path + "/items/Mythic/" + random.choice(os.listdir(self.assets_path + "/items/Mythic")))

        ## objets à ajouter à cause d'autre éléments du build

        # starter = tear -> manamune ou archangel
        if dico["starter"].split("/")[-1] == "tear.png":
            dico["items"].append(self.assets_path + "/items/Other/" + random.choice(["Manamune_item.png", "Archangels_Staff_item.png"]))

        # rune timing parfait -> zhonya ou GA
        runes_names = [rune.split("/")[-1] for rune in dico["runes"][1:6]]
        for rune_name in runes_names:
            if rune_name == "Perfect_Timing_rune.png":
                dico["items"].append(self.assets_path + "/items/Other/" + random.choice(["Zhonyas_Hourglass_item.png", "Guardian_Angel_item.png"]))
                break


        list_of_all_item = os.listdir(self.assets_path + "/items/Other")

        if dico["champion"].split("/")[-1] not in data_lol.range_champion:
            list_of_all_item.remove("Runaans_Hurricane_item.png")
        
        if dico["lane"] != 5:
            list_of_all_item.remove("Vigilant_Wardstone_item.png")


        while len(dico["items"]) != 6:
            item = random.choice(list_of_all_item)

            if self.can_i_add_this_item(dico["items"], item):
                dico["items"].append(self.assets_path + "/items/Other/" + item)

            list_of_all_item.remove(item)
            
        dico["lane"] = self.assets_path + f"/lane/{dico['lane']}.png"

        return dico


    def can_i_add_this_item(self, my_items: list[str], item: str) -> bool:
        if item in data_lol.incompatible_items:
            
            items_constraint = data_lol.incompatible_items[item]

            for item_constraint in items_constraint:
                if item_constraint in my_items:
                    return False

        return True


    def randomizer_image(self, lane, champion):
        dico = self.build(lane, champion)
        image = Image.new("RGBA", (400, 420))

        # image du champion
        champion_image = Image.open(dico["champion"]).resize((100, 100))
        image.paste(champion_image, (10, 10))

        # image de la lane
        lane_image = Image.open(dico["lane"]).resize((50, 50))
        image.paste(lane_image, (125, 35))

        # image du cadre en or de l'objet mythique
        x = 72
        if dico["lane"].split("/")[-1] == "5.png":
            x += 65
        if dico["champion"].split("/")[-1] == "cassiopeia.png":
            x -= 65
        cadre_image = Image.open(self.assets_path + "/images_background/cadre.png")
        image.paste(cadre_image, (x, 347))

        # image des summoners
        x = 7
        for summoner in dico["summoners"]:
            summoner_image = Image.open(summoner).resize((50, 50))
            image.paste(summoner_image, (x, 115))
            x += 55

        # image starter
        max_text_image = Image.open(self.assets_path + "/images_background/starter.png").resize((90, 20))
        image.paste(max_text_image, (10, 210))
        max_item_image = Image.open(dico["starter"]).resize((50, 50))
        image.paste(max_item_image, (115, 195))

        # image max
        max_text_image = Image.open(self.assets_path + "/images_background/max.png").resize((52, 17))
        image.paste(max_text_image, (13, 270))
        max_item_image = Image.open(self.assets_path + "/spells/" + random.choice(os.listdir(self.assets_path + "/spells"))).resize(
            (30, 30))
        image.paste(max_item_image, (125, 263))

        # images runes
        # rune grosse principal
        main_runes = Image.open(dico["runes"][0]).resize((100, 100))
        image.paste(main_runes, (190, 10))

        y = 110
        # runes petites principal
        for rune in dico["runes"][1:4]:
            rune_image = Image.open(rune).resize((50, 50))
            image.paste(rune_image, (215, y))
            y += 65

        # runes secondaire
        y = 110
        for rune in dico["runes"][4:6]:
            rune_image = Image.open(rune).resize((50, 50))
            image.paste(rune_image, (280, y))
            y += 65

        # runes bonus
        y = 110
        for rune in dico["runes"][6:]:
            rune_image = Image.open(rune).resize((50, 50))
            image.paste(rune_image, (345, y))
            y += 65

        # images des items
        x = 10
        for item in dico["items"]:
            item_image = Image.open(item).resize((60, 60))
            image.paste(item_image, (x, 350))
            x += 65

        name = "".join(random.sample("1234567890", 10)) + ".png"
        image.save(os.path.join(self.utils.bot_path(), "tmp", name))
        return os.path.join(self.utils.bot_path(), "tmp", name)


async def setup(bot):
    await bot.add_cog(Randomizer(bot))