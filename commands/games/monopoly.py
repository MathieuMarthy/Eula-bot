import discord
from discord import app_commands
from discord.ext import commands
from commands.games.monopolyClasses.board import Board

from functions import Utils

class Monopoly(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)


    async def command(self, ctx: commands.Context):
        players = [ctx.author]

        board = Board(10, players)
       
        # show players emojis
        embed = self.embedPlayersEmojis(board)
        await ctx.send(embed=embed)

        game_msg = await ctx.send("Chargement...")

        # game loop
        while board.lap <= board.maxLap:
            embed = self.getView(board)

            await game_msg.edit(embed=embed)
            break

    
    def getView(self, board: Board) -> discord.Embed:

        embed = discord.Embed(title=f"tour {board.lap}/{board.maxLap}", color=0xffffff)

        embed.add_field(name="Plateau", value=board.getBoardStr(), inline=False)

        return embed

        
    def embedPlayersEmojis(self, board: Board) -> discord.Embed:
        embed = discord.Embed(title="Joueurs", color=0xffffff)

        for player in board.players:
            embed.add_field(name=player.discord.display_name, value=player.emoji, inline=True)

        return embed


    @commands.command()
    async def monopoly(self, ctx):
        await self.command(ctx)


    @app_commands.command(name="monopoly", description="monopoly jusqu'à 4 joueurs")
    async def monopolySlash(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx)


async def setup(bot):
    await bot.add_cog(Monopoly(bot))
