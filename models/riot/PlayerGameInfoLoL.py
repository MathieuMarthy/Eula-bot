from enum import Enum


class GameStatus(Enum):
    WIN = "WIN"
    LOSE = "LOSE"
    REMAKE = "REMAKE"
    

class PlayerGameInfoLoL:

    def __init__(self, json: dict, puuid: str):
        self.gameDuration = json["info"]["gameDuration"]

        player_index = json["metadata"]["participants"].index(puuid)

        if player_index < 0:
            raise ValueError("Player not found in match")

        player = json["info"]["participants"][player_index]

        self.championName = player["championName"]
        self.isWin = player["win"]

        self.kills = player["kills"]
        self.deaths = player["deaths"]
        self.assists = player["assists"]
        
        if self.gameDuration < 180:
            self.status = GameStatus.REMAKE.value
        elif self.isWin:
            self.status = GameStatus.WIN.value
        else:
            self.status = GameStatus.LOSE.value
