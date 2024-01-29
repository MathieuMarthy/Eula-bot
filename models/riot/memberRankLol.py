import time
from models.riot.rankData import Rank, RankEnum


class MemberRankLol:

    def __init__(self, discordId: int, puuid: str, playerId: str, riotName: str, tag: str) -> None:
        # ids
        self.discordId = discordId
        self.puuid = puuid
        self.playerId = playerId
        self.riotName = riotName
        self.tag = tag.upper()

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
                self.division = self._division_str_to_int(queue["rank"])
                self.lp = queue["leaguePoints"]
                self.wins = queue["wins"]
                self.losses = queue["losses"]
                self.winrate = round(self.wins / (self.wins + self.losses) * 100, 2)
                self.lastUpdate = int(time.time())
                break

    def _division_str_to_int(self, division: str) -> int:
        if division == "I":
            return 1
        if division == "II":
            return 2
        if division == "III":
            return 3
        if division == "IV":
            return 4
        return 0

    def get_division(self) -> str:
        if self.division == 1:
            return "I"
        if self.division == 2:
            return "II"
        if self.division == 3:
            return "III"
        if self.division == 4:
            return "IV"
        return " "
    
    def set_profile_icon_id(self, profile_icon_id: int):
        self.profileIconId = profile_icon_id
    
    def to_json(self) -> dict:
        return {
            "puuid": self.puuid,
            "accountId": self.playerId,
            "riotName": self.riotName,
            "tag": self.tag,
            "rank": self.rank.to_json(),
            "division": self.division,
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
                return False
            if self.division < other.division:
                return True

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
    def from_json(json: dict, discordId: int) -> "MemberRankLol":
        member = MemberRankLol(discordId, json["puuid"], json["accountId"], json["riotName"], json.get("tag", "EUW"))
        member.rank = Rank.from_json(json.get("rank", None))
        member.division = json.get("division", 0)
        member.lp = json.get("lp", 0)
        member.wins = json.get("wins", 0)
        member.losses = json.get("losses", 0)
        member.winrate = json.get("winrate", 0)
        member.lastUpdate = json.get("lastUpdate", 0)
        member.lastGame = json.get("lastGame", 0)
        member.profileIconId = json.get("profileIconId", 0)
        return member
