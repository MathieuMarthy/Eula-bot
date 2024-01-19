import json
import os
from typing import Optional

from data.config import path
from models.riot.memberRankLol import MemberRankLol


class RankLolDao:
    __instance = None
    path = os.path.join(path, "databases", "rank_lol.json")
    rank: dict

    @staticmethod
    def get_instance():
        if RankLolDao.__instance is None :
            RankLolDao.__instance = RankLolDao()
        return RankLolDao.__instance
    

    def __init__(self) -> None:
        self.load()
    

    def load(self):
        try:
            self.ranks = json.loads(open(self.path, "r", encoding="utf-8"))
        except:
            self.ranks = {}
            self.save()


    def save(self):
        json.dump(self.ranks, open(self.path, "w", encoding="utf-8"), indent=4)


    def store_member(self, guildId: int, memberLol: MemberRankLol):
        # Create a new guild if it doesn't exist
        self.ranks[guildId] = self.ranks.get(guildId, {})

        # Store the member
        self.ranks[guildId][memberLol.discordId] = memberLol.to_json()
        self.save()


    def get_member(self, guildId: int, discordId: int) -> Optional[MemberRankLol]:
        json_memberRank = self.ranks.get(guildId, {}).get(discordId, None)

        if json_memberRank is None:
            return None

        return MemberRankLol.from_json(json_memberRank)


    def get_all_members_from_guild(self, guildId: int) -> list[MemberRankLol]:
        return [MemberRankLol.from_json(player_json) for player_json in self.ranks.get(guildId, {}).items()]
    

    def get_server_leaderboard(self, guildId: int) -> list[MemberRankLol]:
        return sorted(self.get_all_members_from_guild(guildId))
