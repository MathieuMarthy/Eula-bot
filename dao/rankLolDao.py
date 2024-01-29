import json
import os
from json import JSONDecodeError
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
        self.ranks: dict[int, dict[int, list[MemberRankLol]]] = {}
        self.load()

    def load(self):
        try:
            data = json.load(open(self.path, "r", encoding="utf-8"))
        except JSONDecodeError:
            data = {}

        for guildId, members in data.items():
            guildId = int(guildId)
            self.ranks[guildId] = {}

            self.ranks[guildId] = {
                int(discordId): [MemberRankLol.from_json(member, int(discordId)) for member in members]
                for discordId, members in members.items()
            }

    def save(self):
        json.dump(self.ranks, open(self.path, "w", encoding="utf-8"), indent=4, default=lambda o: o.to_json() if isinstance(o, MemberRankLol) else o)

    def store_member(self, guildId: int, memberLol: MemberRankLol):
        self.ranks[guildId] = self.ranks.get(guildId, {})

        if memberLol.discordId in self.ranks[guildId]:

            # if the account is already stored, we remove it
            for riot_account in self.ranks[guildId][memberLol.discordId]:
                if riot_account.playerId == memberLol.playerId:
                    self.ranks[guildId][memberLol.discordId].remove(riot_account)
                    break

            # then we add the new account
            self.ranks[guildId][memberLol.discordId].append(memberLol)
        else:
            self.ranks[guildId][memberLol.discordId] = [memberLol]
        self.save()

    def get_member_accounts(self, guildId: int, discordId: int) -> list[MemberRankLol]:
        return self.ranks.get(guildId, {}).get(discordId, [])

    def get_all_members_from_guild(self, guildId: int) -> list[MemberRankLol]:
        riot_accounts = []
        for member in self.ranks.get(guildId, {}).values():
            riot_accounts.extend(member)

        return riot_accounts

    def get_server_leaderboard(self, guildId: int) -> list[MemberRankLol]:
        return sorted(self.get_all_members_from_guild(guildId))


    def remove_member_by_name(self, guildId: int, discordId: int, name: str) -> bool:
        if discordId not in self.ranks.get(guildId, {}):
            return False

        for member in self.ranks[guildId][discordId]:
            if member.riotName.lower() == name.lower():
                self.ranks[guildId][discordId].remove(member)
                self.save()
                return True

        return False
