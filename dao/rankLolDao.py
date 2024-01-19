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
        self.ranks: dict[int, dict[int, MemberRankLol]] = {}
        self.load()
    

    def load(self):
        data = json.load(open(self.path, "r", encoding="utf-8"))
        for guildId, members in data.items():
            self.ranks[guildId] = {
                int(discordId): MemberRankLol.from_json(member)
                for discordId, member in members.items()
            }


    def save(self):
        json.dump(self.ranks, open(self.path, "w", encoding="utf-8"), indent=4, default=lambda o: o.to_json() if isinstance(o, MemberRankLol) else o)


    def store_member(self, guildId: int, memberLol: MemberRankLol):
        """Store a member in the database

        Args:
            guildId (int): The id of the guild
            memberLol (MemberRankLol): The member to store

        Raises:
            DbAlreadyExistsError: If the member is already registered
        """

        # Create a new guild if it doesn't exist
        self.ranks[guildId] = self.ranks.get(guildId, {})

        # Store the member
        self.ranks[guildId][memberLol.discordId] = memberLol
        self.save()


    def get_member(self, guildId: int, discordId: int) -> Optional[MemberRankLol]:
        return self.ranks.get(guildId, {}).get(discordId, None)


    def get_all_members_from_guild(self, guildId: int) -> list[MemberRankLol]:
        return [player for player in self.ranks.get(guildId, {}).values()]
    

    def get_server_leaderboard(self, guildId: int) -> list[MemberRankLol]:
        return sorted(self.get_all_members_from_guild(guildId))
