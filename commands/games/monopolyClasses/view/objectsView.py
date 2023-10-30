import discord
from discord.ui import View, Select, Button

from commands.games.monopolyClasses.object import Object
from commands.games.monopolyClasses.player import Player

class ObjectsView(View):
    
    def __init__(self, player: Player, objects: list[Object], yesFunc: callable, noFunc: callable, buyPhase: bool):
        super().__init__(timeout=None)
        self.player = player
        self.yesFunc = yesFunc
        self.noFunc = noFunc

        # Select
        self.select = Select(placeholder="Sélectionnez un objet", row=1)

        for obj in objects:
            if buyPhase:
                self.select.add_option(label=f"{obj.name} - {obj.price} $", value=obj.id)
            else:
                self.select.add_option(label=obj.name, value=obj.id)

        self.select.callback = self.select_callback
        self.add_item(self.select)

        # Buttons
        if buyPhase:
            self.yesButton = Button(label="Acheter", style=discord.ButtonStyle.green, row=2)
        else:
            self.yesButton = Button(label="Utiliser", style=discord.ButtonStyle.green, row=2)

        self.yesButton.callback = self.yes
        self.add_item(self.yesButton)

        self.noButton = Button(label="Fermer", style=discord.ButtonStyle.red, row=2)
        self.noButton.callback = self.cancel
        self.add_item(self.noButton)


    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.player.discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return

        await interaction.response.defer()


    async def yes(self, interaction: discord.Interaction):
        await self.yesFunc(interaction, int(self.select.values[0]))


    async def cancel(self, interaction: discord.Interaction):
        await self.noFunc(interaction)
