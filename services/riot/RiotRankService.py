from typing import Optional
from services.riot.RiotApi import RiotApi
from dao.rankLolDao import RankLolDao
from models.riot.memberRankLol import MemberRankLol


class RiotRankService:

    def __init__(self) -> None:
        self.riot_api = RiotApi()
        self.riot_dao = RankLolDao.get_instance()

    def store_member_by_name_and_tag(self, guildId: int, discordId: int, name: str, tag: str) -> MemberRankLol:
        puuid, riot_name = self.riot_api.get_player_puuid_name(name, tag)

        player_id, ppId = self.riot_api.get_player_id_ppId(puuid)
        rank_data = self.riot_api.get_rank_data(player_id)

        memberRankLol = self.store_player(guildId, discordId, player_id, puuid, riot_name, rank_data, ppId)
        return memberRankLol

    def store_player(self, guildId: int, discordId: int, player_id: str, puuid: str, riotName: str,
                     rank_data: Optional[list[dict]] = None, profile_icon_id: Optional[int] = None):
        memberRankLol = MemberRankLol(discordId, player_id, puuid, riotName)

        if profile_icon_id is not None:
            memberRankLol.set_profile_icon_id(profile_icon_id)

        if rank_data is not None:
            memberRankLol.fill_from_raw_rank_data(rank_data)

        self.riot_dao.store_member(guildId, memberRankLol)
        return memberRankLol

    def get_member_accounts(self, guildId: int, discordId: int) -> list[MemberRankLol]:
        return self.riot_dao.get_member_accounts(guildId, discordId)

    def update_player_data(self, memberRankLol: MemberRankLol):
        rank_data = self.riot_api.get_rank_data(memberRankLol.accountId)

        if rank_data is None:
            return

        memberRankLol = memberRankLol.fill_from_raw_rank_data(rank_data)

        self.riot_dao.store_member(memberRankLol)

    def update_players_data(self, players: list[MemberRankLol]):
        for player in players:
            self.update_player_data(player)

    def get_server_leaderboard(self, guildId: int) -> list[MemberRankLol]:
        return self.riot_dao.get_server_leaderboard(guildId)

    def get_icone_url(self, icon_id: int) -> str:
        return self.riot_api.get_profile_icon_url(icon_id)

    def remove_member_by_name(self, guildId: int, discordId: int, name: str) -> bool:
        return self.riot_dao.remove_member_by_name(guildId, discordId, name)
