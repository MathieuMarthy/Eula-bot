import time
from models.riot.rankData import Rank, RankEnum


class MemberRankLol:

    def __init__(self, discordId: int, puuid: str, accountId: str, riotName: str) -> None:
        # ids
        self.discordId = discordId
        self.puuid = puuid
        self.accountId = accountId
        self.riotName = riotName

        # lol data
        self.rank: Rank = RankEnum.UNRANKED
        self.division = 0
        self.lp = 0
        self.wins = 0
        self.losses = 0
        self.winrate = 0.0
        self.lastUpdate = 0
        self.lastGame = 0
        self.profileIconId = 0
    
    def empty_lol_data(self) -> bool:
        return self.rank == RankEnum.UNRANKED \
               and self.division == 0 \
               and self.lp == 0 \
               and self.wins == 0 \
               and self.losses == 0 \
               and self.winrate == 0.0 \
               and self.lastUpdate == 0 \
               and self.lastGame == 0

    def fill_from_raw_rank_data(self, rank_data: list[dict]):
        for queue in rank_data:
            if queue["queueType"] == "RANKED_SOLO_5x5":
                self.rank = Rank.from_string(queue["tier"])
                self.division = queue["rank"]
                self.lp = queue["leaguePoints"]
                self.wins = queue["wins"]
                self.losses = queue["losses"]
                self.winrate = round(self.wins / (self.wins + self.losses) * 100, 2)
                self.lastUpdate = int(time.time())
                break
    
    def set_profile_icon_id(self, profile_icon_id: int):
        self.profileIconId = profile_icon_id
    
    def to_json(self) -> dict:
        return {
            "puuid": self.puuid,
            "accountId": self.accountId,
            "riotName": self.riotName,
            "rank": self.rank.to_json(),
            "lp": self.lp,
            "wins": self.wins,
            "losses": self.losses,
            "winrate": self.winrate,
            "lastUpdate": self.lastUpdate,
            "profileIconId": self.profileIconId
        }
    
    def __lt__(self, other) -> bool:
        if self.__class__ is other.__class__:
            if self.rank > other.rank:
                return True
            if self.rank < other.rank:
                return False

            if self.division > other.division:
                return True
            if self.division < other.division:
                return False

            if self.lp > other.lp:
                return True
            if self.lp < other.lp:
                return False

            if self.wins > other.wins:
                return True
            if self.wins < other.wins:
                return False

            if self.losses < other.losses:
                return True
            if self.losses > other.losses:
                return False

            if self.winrate > other.winrate:
                return True
            if self.winrate < other.winrate:
                return False

            return self.riotName < other.riotName
        
        return False 

    @staticmethod
    def from_json(json: dict):
        member = MemberRankLol(json["discordId"], json["puuid"], json["accountId"], json["riotName"])
        member.rank = Rank.from_json(json.get("rank", None))
        member.lp = json.get("lp", 0)
        member.wins = json.get("wins", 0)
        member.losses = json.get("losses", 0)
        member.winrate = json.get("winrate", 0)
        member.lastUpdate = json.get("lastUpdate", 0)
        member.lastGame = json.get("lastGame", 0)
        member.profileIconId = json.get("profileIconId", 0)
        return member
