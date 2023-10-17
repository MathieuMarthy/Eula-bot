from asyncio import sleep as async_sleep
import discord
from discord.ui import View, Button

from commands.games.monopolyClasses.board import Board
from commands.games.monopolyClasses.data.squareData import SquareType
from commands.games.monopolyClasses.square import Property, Tax
from commands.games.monopolyClasses.view.BuyView import BuyView
from commands.games.monopolyClasses.view.upgradeView import UpgradeView
from functions import Utils

class BoardView(View):
    def __init__(self, board: Board, game_msg: discord.Message):
        super().__init__(timeout=None)
        self.board = board
        self.game_msg = game_msg
        self.embed_color = 0x989eec

        self.buy_view = BuyView(self.buyFunc, self.noFunc)
        self.popup_msg = None
        self.can_roll_dice = True
        self.userHasRolled = False



    @discord.ui.button(label="Lancer les dés", custom_id="dice", style=discord.ButtonStyle.primary, emoji="🎲")
    async def dice_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.board.getCurrentPlayer().discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return
        
        if self.userHasRolled:
            await interaction.response.send_message("Vous avez déjà lancé les dés !", ephemeral=True)
            return
        
        if not self.can_roll_dice:
            await interaction.response.send_message("Vous ne pouvez pas lancer les dés maintenant !", ephemeral=True)
            return

        self.can_roll_dice = False
        await interaction.response.defer()
        dice = self.board.rollDice()

        square = self.board.getSquareUnderPlayer(self.board.getCurrentPlayer())
        await self.showAction(f"<a:roll_dice:1162800533548056707> Vous avez obtenu {dice} !\n \
            Vous êtes sur la case {square.name}")
        await async_sleep(3)

        await self.executeSquare()


    @discord.ui.button(label="Augmenter les loyers", custom_id="upgrade", style=discord.ButtonStyle.secondary, emoji="📈")
    async def upgrade_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.board.getCurrentPlayer().discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return

        
        user = self.board.getCurrentPlayer()
        upgradePrice = user.getPriceForUpgrade()

        if upgradePrice > user.money:
            await interaction.response.send_message(f"Vous n'avez pas assez d'argent !\nIl vous faut **{upgradePrice} $**", ephemeral=True)
            return
    
        if user.getNumberOfProperties() == 0:
            await interaction.response.send_message(f"Vous n'avez aucune propriété !", ephemeral=True)
            return
        
        await interaction.response.defer()
        self.can_roll_dice = False
        embed = discord.Embed(title=f"Amélioration", description=f"Voulez-vous améliorer le loyer de 20% pour toutes vos propriétés actuelles pour **{upgradePrice} $** ?", color=self.embed_color)
        self.popup_msg = await self.game_msg.channel.send(embed=embed, view=UpgradeView(self.upgradeFunc, self.noFunc))


    @discord.ui.button(label="Finir le tour", custom_id="next", style=discord.ButtonStyle.red, emoji="⏭️")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.board.getCurrentPlayer().discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return
    
        if not self.userHasRolled:
            await interaction.response.send_message("Vous devez lancer les dés !", ephemeral=True)
            return

        await interaction.response.defer()
        await self.nextPlayer()


    async def executeSquare(self):
        """When a player go on a square"""

        square = self.board.getSquareUnderPlayer(self.board.getCurrentPlayer())

        # 🏠 & 🚂
        if square.type == SquareType.PROPERTY.value or square.type == SquareType.RAILROAD.value:
            
            if self.board.getOwner(square) != None:
                playerHasPaid, square_rent = self.board.playerPayRent(self.board.getCurrentPlayer(), square)

                await self.showAction(f"Vous avez payé **{square_rent} $** de loyer à {self.board.getOwner(square).discord.display_name} !")
                
                if not playerHasPaid:
                    # TODO : player has not enough money
                    await self.showAction(f"Vous n'avez pas assez d'argent pour payer le loyer !")
                    pass

            else:
                embed = discord.Embed(title=f"Achat", description=f"Voulez-vous acheter **{square.name}** pour **{square.price} $**", color=self.embed_color)
                view = self.buy_view

                self.popup_msg = await self.game_msg.channel.send(embed=embed, view=view)
                return

        # 🍀
        elif square.type == SquareType.LUCK.value:
            action = self.board.luck(self.board.getCurrentPlayer())
            await self.showAction(action)
            await async_sleep(2)

        # ⛓
        elif square.type == SquareType.GO_TO_JAIL.value:
            user = self.board.getCurrentPlayer()
            old_position = user.position

            user.goToJail()
            self.board.movePlayerOnBoard(user, old_position)

            await self.showAction("Vous allez en prison !")

        # 💰
        elif square.type == SquareType.TAX.value:
            square: Tax
            self.board.getCurrentPlayer().loseMoney(square.price)
            await self.showAction(f"Vous avez payé **{square.price} $** de taxe !")

        self.userHasRolled = True
        await async_sleep(3)
        await self.showAction("...")


    async def showAction(self, action: str):
        await self.game_msg.edit(embed=self.getEmbed(action))


    def getEmbed(self, action: str = "...") -> discord.Embed:

        # embed
        embed = discord.Embed(title=f"Monopoly", color=self.embed_color)
        embed.add_field(name="Plateau", value=self.board.getBoardStr(), inline=False)
        
        currentPlayer = self.board.getCurrentPlayer()
        embed.add_field(name="Au tour de", value=f"{currentPlayer.discord.display_name} - {currentPlayer.money} $", inline=False)
        embed.add_field(name="Actions", value=action)
        
        return embed


    async def nextPlayer(self):
        self.board.nextPlayer()
        self.can_roll_dice = True
        self.userHasRolled = False
        await self.game_msg.edit(embed=self.getEmbed())


    async def buyFunc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.board.getCurrentPlayer().discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return

        user = self.board.getCurrentPlayer()
        square = self.board.getSquareUnderPlayer(user)
        self.board.buyProperty(user, square)
        
        await self.popup_msg.delete()

        await self.showAction(f"Vous avez acheté **{square.name}** !")
        await async_sleep(3)
        await self.showAction("...")
        self.userHasRolled = True


    async def upgradeFunc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.board.getCurrentPlayer().discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return
    
        self.can_roll_dice = True
        self.board.getCurrentPlayer().upgradeProperties()
        await self.popup_msg.delete()
        await self.showAction(f"Vous avez amélioré toutes vos propriétés !")


    async def noFunc(self, interaction: discord.Interaction, button: discord.ui.Button, text: str):
        if interaction.user != self.board.getCurrentPlayer().discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return

        await self.showAction(text)
        await self.popup_msg.delete()
        await async_sleep(3)
