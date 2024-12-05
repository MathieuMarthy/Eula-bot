from typing import Tuple, Callable

import discord as lib_discord
import discord.ui
from discord import app_commands
from discord.ext import commands

from services.general.viewPages.ViewPages import ViewPages
from services.riot.RiotRankService import RiotRankService
from errors.api import ApiError
from models.riot.memberRankLol import MemberRankLol


class LolRank(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.riotService = RiotRankService()

    def create_player_embed(self, memberRankLol: MemberRankLol) -> lib_discord.Embed:
        if memberRankLol.empty_lol_data():
            embed = lib_discord.Embed(
                title=f"{memberRankLol.riotName}#{memberRankLol.tag}",
                description="Unranked",
                color=0x000000
            )
            embed.set_thumbnail(url=self.riotService.get_icone_url(memberRankLol.profileIconId))
            return embed

        embed = lib_discord.Embed(
            title=f"{memberRankLol.riotName}#{memberRankLol.tag}",
            description=f"{memberRankLol.rank.emote} {memberRankLol.rank.name} {memberRankLol.get_division()} {memberRankLol.lp} LP",
            color=int(memberRankLol.rank.color, 16)
        )
        embed.add_field(name="Winrate", value=f"{memberRankLol.winrate}%")
        embed.add_field(name="Wins", value=memberRankLol.wins)
        embed.add_field(name="Losses", value=memberRankLol.losses)
        embed.set_thumbnail(url=self.riotService.get_icone_url(memberRankLol.profileIconId))

        return embed

    @app_commands.command(name="add_lol_account", description="enregistre un compte LoL sur le serveur")
    @app_commands.describe(riot_name="votre nom d'invocateur")
    @app_commands.describe(tag="votre tag")
    @app_commands.describe(discord="compte discord du joueur, par défaut votre compte")
    async def register(self, interaction: lib_discord.Interaction, riot_name: str, tag: str,
                       discord: lib_discord.Member = None):
        try:
            discord_id = interaction.user.id if discord is None else discord.id

            memberRankLol = self.riotService.store_member_by_name_and_tag(
                interaction.guild_id,
                discord_id,
                riot_name,
                tag
            )
        except ApiError as e:
            await interaction.response.send_message(f"Erreur:\n{e}", ephemeral=True)
            return
        except Exception as e:
            await interaction.response.send_message(f"Une erreur est survenue:\n{e}", ephemeral=True)
            return

        embed = self.create_player_embed(memberRankLol)

        await interaction.response.send_message(embed=embed, content=None)

    @app_commands.command(name="lol_leaderboard", description="affiche le leaderboard des joueurs du serveur")
    async def leaderboard(self, interaction: lib_discord.Interaction):
        await interaction.response.defer(ephemeral=False, thinking=True)

        self.riotService.update_players_data(interaction.guild_id)
        membersRank = self.riotService.get_server_leaderboard(interaction.guild_id)

        viewPages = ViewPages(
            interaction,
            f"Leaderboard de {interaction.guild.name}",
            membersRank,
            10,
            lambda
                memberRankLol: f"{memberRankLol.riotName} - {memberRankLol.rank.emote} {memberRankLol.rank.name} {memberRankLol.get_division()} {memberRankLol.lp} LP - <@{memberRankLol.discordId}>",
            defer_was_called_on_interaction=True
        )
        await viewPages.start()

    @app_commands.command(name="show_lol_rank", description="affiche le rank LoL d'un joueur")
    @app_commands.describe(discord="compte discord du joueur, par défaut votre compte")
    async def show_rank(self, interaction: lib_discord.Interaction, discord: lib_discord.Member):
        discord_id = interaction.user.id if discord is None else discord.id

        memberLolAccounts = self.riotService.get_member_accounts(interaction.guild_id, discord_id)

        if len(memberLolAccounts) == 0:
            await interaction.response.send_message("Ce joueur n'est pas enregistré", ephemeral=True)
            return

        async def send_message(embeds_to_send: list[lib_discord.Embed]):
            if len(embeds_to_send) != len(memberLolAccounts):
                return await interaction.followup.send(embeds=embeds_to_send, content=None)

            return await interaction.response.send_message(embeds=embeds_to_send, content=None)

        embeds = []
        for account in memberLolAccounts:
            embeds.append(self.create_player_embed(account))

            if len(embeds) == 10:
                await send_message(embeds)

        if embeds:
            await send_message(embeds)

    @app_commands.command(name="remove_lol_account", description="supprime un compte LoL")
    @app_commands.describe(riot_name="le nom du compte à supprimer")
    async def remove_account(self, interaction: lib_discord.Interaction, riot_name: str):
        memberRankLol = self.riotService.remove_member_by_name(interaction.guild_id, interaction.user.id, riot_name)

        if not memberRankLol:
            await interaction.response.send_message("Ce compte n'est pas enregistré", ephemeral=True)
            return

        await interaction.response.send_message(f"Le compte **{riot_name}** n'est plus lié à votre compte",
                                                ephemeral=True)


async def setup(bot):
    await bot.add_cog(LolRank(bot))
