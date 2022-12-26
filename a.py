from assets.League_of_legends import data_lol

champions = data_lol.melee_champion + data_lol.range_champion

champions.sort()

for champion in champions:
    print(champion.replace(".png", "").capitalize())
