from asyncio import sleep as async_sleep
import discord
from discord.ui import View, Button

from commands.games.monopolyClasses.board import Board
from commands.games.monopolyClasses.data.squareData import SquareType
from commands.games.monopolyClasses.square import Property, Tax
from commands.games.monopolyClasses.view.BuyView import BuyView
from functions import Utils

class BoardView(View):
    def __init__(self, board: Board, game_msg: discord.Message):
        super().__init__(timeout=None)
        self.board = board
        self.game_msg = game_msg
        self.embed_color = 0x989eec
        self.buy_view = BuyView(self.buyFunc, self.noFunc)
        self.buy_msg = None


    @discord.ui.button(label="Lancer les dés", custom_id="dice", style=discord.ButtonStyle.primary, emoji="🎲")
    async def dice_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.board.getCurrentPlayer().discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return

        await interaction.response.defer()
        dice = self.board.rollDice()

        square = self.board.getSquareUnderPlayer(self.board.getCurrentPlayer())
        await self.showAction(f"<a:roll_dice:1162800533548056707> Vous avez obtenu {dice} !\n \
            Vous êtes sur la case {square.name}")
        await async_sleep(3)

        await self.executeSquare()


    async def executeSquare(self):
        """When a player go on a square"""

        square = self.board.getSquareUnderPlayer(self.board.getCurrentPlayer())

        # 🏠 & 🚂
        if square.type == SquareType.PROPERTY.value or square.type == SquareType.RAILROAD.value:
            
            if self.board.getOwner(square) != None:
                playerHasPaid = self.board.playerPayRent(self.board.getCurrentPlayer(), square)
                
                if not playerHasPaid:
                    # TODO : player has not enough money
                    pass

            else:
                embed = discord.Embed(title=f"Achat", description=f"Voulez-vous acheter **{square.name}** pour **{square.price} $**", color=self.embed_color)
                view = self.buy_view

                self.buy_msg = await self.game_msg.channel.send(embed=embed, view=view)

        # 🍀
        elif square.type == SquareType.LUCK.value:
            self.board.luck(self.board.getCurrentPlayer())

        # ⛓
        elif square.type == SquareType.GO_TO_JAIL.value:
            self.board.getCurrentPlayer().goToJail()

        # 💰
        elif square.type == SquareType.TAX.value:
            square: Tax
            self.board.getCurrentPlayer().loseMoney(square.price)


    async def showAction(self, action: str):
        await self.game_msg.edit(embed=self.getEmbed(action))


    def getEmbed(self, action: str = None) -> discord.Embed:

        # embed
        embed = discord.Embed(title=f"tour {self.board.lap}/{self.board.maxLap}", color=self.embed_color)
        embed.add_field(name="Plateau", value=self.board.getBoardStr(), inline=False)
        
        currentPlayer = self.board.getCurrentPlayer()
        embed.add_field(name="Au tour de", value=f"{currentPlayer.discord.display_name} - {currentPlayer.money} $", inline=False)
        embed.add_field(name="Actions", value=action if action else f"...")
        
        return embed


    async def nextPlayer(self):
        self.board.nextPlayer()
        await self.game_msg.edit(embed=self.getEmbed())


    async def buyFunc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.board.getCurrentPlayer().discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return

        user = self.board.getCurrentPlayer()
        user.buyProperty(self.board.getSquareUnderPlayer(user))
        await self.buy_msg.delete()

        await self.showAction("Vous avez acheté la case !")
        await async_sleep(3)
        await self.nextPlayer()


    async def noFunc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.board.getCurrentPlayer().discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return

        await self.showAction("Vous n'avez pas acheté la case !")
        await async_sleep(3)
        await self.nextPlayer()
