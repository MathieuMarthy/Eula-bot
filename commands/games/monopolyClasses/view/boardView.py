from asyncio import sleep as async_sleep
import discord
from discord.ui import View, Button

from commands.games.monopolyClasses.board import Board
from functions import Utils

class BoardView(View):
    def __init__(self, board: Board, game_msg: discord.Message):
        super().__init__(timeout=None)
        self.board = board
        self.game_msg = game_msg
        self.embed_color = 0x989eec


    @discord.ui.button(label="Lancer les dés", custom_id="dice", style=discord.ButtonStyle.primary, emoji="🎲")
    async def dice_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        dice = self.board.rollDice()
        await self.showAction(f"<a:roll_dice:1162800533548056707> Vous avez obtenu {dice} !\n \
            Vous êtes sur la case {self.board.getSquareUnderPlayer(self.board.getCurrentPlayer()).name}")
        await async_sleep(3)

        # effet de la case

    async def showAction(self, action: str):
        await self.game_msg.edit(embed=self.getEmbed(action))


    def getEmbed(self, action: str = None) -> discord.Embed:

        # embed
        embed = discord.Embed(title=f"tour {self.board.lap}/{self.board.maxLap}", color=self.embed_color)
        embed.add_field(name="Plateau", value=self.board.getBoardStr(), inline=False)
        
        currentPlayer = self.board.getCurrentPlayer()
        embed.add_field(name="Au tour de:", value=f"{currentPlayer.discord.display_name} - {currentPlayer.money} $", inline=False)
        embed.add_field(name="Actions", value=action if action else f"...")
        
        return embed
