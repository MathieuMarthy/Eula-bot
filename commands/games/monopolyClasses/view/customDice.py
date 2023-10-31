import discord
from discord.ui import View, Select

from commands.games.monopolyClasses.player import Player


class CustomDiceView(View):

    def __init__(self, player: Player, rollDiceFunc: callable):
        super().__init__(timeout=None)
        self.player = player
        self.rollDiceFunc = rollDiceFunc

        self.select = Select(placeholder="Choisissez le résultat de votre prochain lancer de dé")

        for i in range(1, 13):
            self.select.add_option(label=str(i), value=str(i))
        
        self.select.callback = self.select_callback
        self.add_item(self.select)

    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user != self.player.discord:
            await interaction.response.send_message("Ce n'est pas votre tour !", ephemeral=True)
            return

        await interaction.response.defer()
        await self.rollDiceFunc(int(self.select.values[0]))
