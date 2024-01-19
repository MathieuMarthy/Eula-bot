import discord
from discord import app_commands
from discord.ext import commands

from services.riot.RiotRankService import RiotRankService
from errors.api import ApiError, ApiNotFoundError
from models.riot.memberRankLol import MemberRankLol


class LolRank(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.riotService = RiotRankService()

    def create_player_embed(self, memberRankLol: MemberRankLol) -> discord.Embed:
        if memberRankLol.empty_lol_data():
            embed = discord.Embed(
                title=memberRankLol.riotName,
                description="Unranked",
                color=int(memberRankLol.rank.color, 16)
            )
            embed.set_thumbnail(url=self.riotService.get_icone_url(memberRankLol.profileIconId))
            return embed

        embed = discord.Embed(
            title=memberRankLol.riotName,
            description=f"{memberRankLol.rank.name} {memberRankLol.division} {memberRankLol.lp} LP",
            color=int(memberRankLol.rank.color, 16)
        )
        embed.add_field(name="Winrate", value=f"{memberRankLol.winrate}%")
        embed.add_field(name="Wins", value=memberRankLol.wins)
        embed.add_field(name="Losses", value=memberRankLol.losses)
        embed.add_field(name="Last game", value=memberRankLol.lastGame)
        embed.set_thumbnail(url=self.riotService.get_icone_url(memberRankLol.profileIconId))

        return embed

    @app_commands.command(name="lol_register", description="enregistre votre compte LoL")
    @app_commands.describe(riot_name="votre nom d'invocateur")
    @app_commands.describe(tag="votre tag")
    @app_commands.describe(discord="compte discord du joueur, par défaut votre compte")
    async def register(self, interaction: discord.Interaction, riot_name: str, tag: str, discord: discord.Member = None):
        try:
            discord_id = interaction.user.id if discord is None else discord.id

            memberRankLol = self.riotService.store_member_by_name_and_tag(
                interaction.guild_id,
                discord_id,
                riot_name,
                tag
            )
        except ApiNotFoundError:
            await interaction.response.send_message("Impossible de trouver votre compte LoL", ephemeral=True)
            return
        except ApiError:
            await interaction.response.send_message("Erreur de connexion à l'API Riot", ephemeral=True)
            return


        embed = self.create_player_embed(memberRankLol)

        await interaction.response.send_message(embed=embed, content=None)


    @app_commands.command(name="lol_leaderboard", description="affiche le leaderboard des joueurs du serveur")
    async def leaderboard(self, interaction: discord.Interaction):
        pass


async def setup(bot):
    await bot.add_cog(LolRank(bot))
