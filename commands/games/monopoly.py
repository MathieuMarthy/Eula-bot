import discord
from discord import app_commands
from discord.ext import commands

from commands.games.monopolyClasses.board import Board
from commands.games.monopolyClasses.view.boardView import BoardView

class Monopoly(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client


    async def command(self, ctx: commands.Context):
        players = [ctx.author, ctx.guild.get_member(826029326893842463)]
        board = Board(players)
        
        # show players emoji
        await ctx.send(embed=self.embedPlayersEmojis(board))

        # load msg & view
        game_msg = await ctx.send("Chargement...")
        view = BoardView(
            board,
            game_msg
        )

        # show the board / game begin
        await game_msg.edit(content="", embed=view.getEmbed(), view=view)


    def embedPlayersEmojis(self, board: Board) -> discord.Embed:
        embed = discord.Embed(title="Joueurs", color=0x989eec)

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
