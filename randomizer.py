import random
import os
import sys
from PIL import Image
import data_lol

assets_path = os.path.dirname(sys.argv[0]) + "/assets"


def runes() -> list[str]:
    """Retourne la liste des chemins des images de runes random"""
    assets_runes_path = assets_path + "/runes"
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
            assets_path + f"/runes_shards/{i}/" + random.choice(os.listdir(assets_path + f"/runes_shards/{i}")))

    return path_list_of_runes


def champion() -> str:
    return assets_path + "/champions/" + random.choice(os.listdir(assets_path + "/champions"))


def lane():
    """
    1 -> top
    2 -> jungle
    3 -> mid
    4 -> adc
    5 -> support
    """
    return random.randint(1, 5)


def summoners(jungle: bool = False) -> list[str]:
    assets_summoners_path = assets_path + "/summoners"
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


def build(gived_lane: str = "random") -> dict:
    dico = {"champion": champion(), "runes": runes(), "items": [], "summoners": [], "starter": ""}

    if gived_lane in [1, 2, 3, 4, 5]:
        dico["lane"] = gived_lane
    else:
        dico["lane"] = lane()

    dico["summoners"] = summoners(dico["lane"] == 2)

    # starter jungler
    if dico["lane"] == 2:
        dico["starter"] = assets_path + "/smite/" + random.choice(os.listdir(assets_path + "/smite"))

    # starter support
    elif dico["lane"] == 5:
        item_support = random.randint(1, 4)
        dico["starter"] = assets_path + f"/support/{item_support}/start.png"
        dico["items"].append(assets_path + f"/support/{item_support}/final.png")

    # starter
    else:
        dico["starter"] = assets_path + f"/starter/" + random.choice(os.listdir(assets_path + f"/starter"))

    # bottes aléatoire
    if dico["champion"].split("/")[-1] != "Cassiopeia.png":
        dico["items"].append(assets_path + "/items/Boots/" + random.choice(os.listdir(assets_path + "/items/Boots")))

    # mythique aléatoire
    dico["items"].append(assets_path + "/items/Mythic/" + random.choice(os.listdir(assets_path + "/items/Mythic")))

    list_of_all_item = os.listdir(assets_path + "/items/Other")

    if dico["champion"].split("/")[-1] not in data_lol.range_champion:
        list_of_all_item.remove("Runaans_Hurricane_item.png")

    while len(dico["items"]) != 6:
        item = random.choice(list_of_all_item)

        dico["items"].append(assets_path + "/items/Other/" + item)
        list_of_all_item.remove(item)

        for list_of_item in data_lol.incompatible_items:
            if item in list_of_item:

                for incompatible_item in list_of_item:
                    if incompatible_item in list_of_all_item:
                        list_of_all_item.remove(incompatible_item)

    dico["lane"] = assets_path + f"/lane/{dico['lane']}.png"

    return dico


def randomizer_image(lane_of_player="random"):
    dico = build(lane_of_player)
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
    if dico["champion"].split("/")[-1] == "Cassiopeia.png":
        x -= 65
    cadre_image = Image.open(assets_path + "/images_background/cadre.png")
    image.paste(cadre_image, (x, 347))

    # image des summoners
    x = 7
    for summoner in dico["summoners"]:
        summoner_image = Image.open(summoner).resize((50, 50))
        image.paste(summoner_image, (x, 115))
        x += 55

    # image starter
    max_text_image = Image.open(assets_path + "/images_background/starter.png").resize((90, 20))
    image.paste(max_text_image, (10, 210))
    max_item_image = Image.open(dico["starter"]).resize((50, 50))
    image.paste(max_item_image, (115, 195))

    # image max
    max_text_image = Image.open(assets_path + "/images_background/max.png").resize((52, 17))
    image.paste(max_text_image, (13, 270))
    max_item_image = Image.open(assets_path + "/spells/" + random.choice(os.listdir(assets_path + "/spells"))).resize(
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
    image.save(assets_path + f"/pictures/{name}")
    return assets_path + f"/pictures/{name}"
