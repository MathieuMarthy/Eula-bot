

from dataclasses import dataclass
from enum import auto

from discord import Enum


@dataclass
class RankData:
    queueType: str
    tier: str
    rank: str
    leaguePoints: int
    wins: int
    losses: int


class Rank:
    value: int
    name: str
    color: str

    def __init__(self, value: int, name: str, color: str) -> None:
        self.value = value
        self.name = name
        self.color = color
    
    def __lt__(self, other) -> bool:
        if self.__class__ is other.__class__:
            return self.value < other.value
        
        return False

    def __eq__(self, other) -> bool:
        if self.__class__ is other.__class__:
            return self.value == other.value
        
        return False
    
    def to_json(self):
        return {
            "value": self.value,
            "name": self.name,
            "color": self.color
        }
    
    @staticmethod
    def from_json(json: dict):
        if json is None:
            return RankEnum.UNRANKED
        return Rank(
            json["value"],
            json["name"],
            json["color"]
        )
    
    @staticmethod
    def from_string(string: str):
        if string == "IRON":
            return RankEnum.IRON
        elif string == "BRONZE":
            return RankEnum.BRONZE
        elif string == "SILVER":
            return RankEnum.SILVER
        elif string == "GOLD":
            return RankEnum.GOLD
        elif string == "PLATINUM":
            return RankEnum.PLATINUM
        elif string == "DIAMOND":
            return RankEnum.DIAMOND
        elif string == "MASTER":
            return RankEnum.MASTER
        elif string == "GRANDMASTER":
            return RankEnum.GRANDMASTER
        elif string == "CHALLENGER":
            return RankEnum.CHALLENGER
        else:
            return RankEnum.UNRANKED


class RankEnum:
    UNRANKED = Rank(0, "Unranked", "000000")
    IRON = Rank(1, "Iron", "434343")
    BRONZE = Rank(2, "Bronze", "cd7f32")
    SILVER = Rank(3, "Silver", "c0c0c0")
    GOLD = Rank(4, "Gold", "ffd700")
    PLATINUM = Rank(5, "Platinum", "00ffff")
    DIAMOND = Rank(6, "Diamond", "00ff00")
    MASTER = Rank(7, "Master", "ff1493")
    GRANDMASTER = Rank(8, "GrandMaster", "ff0000")
    CHALLENGER = Rank(9, "Challenger", "ff0000")
