import discord
from discord.ui import View

from commands.games.monopolyClasses.player import Player


class SellPropertiesView(View):
    
    def __init__(self, player: Player, sellPropertiesFunc: callable, noFunc: callable):
        super().__init__(timeout=None)
        self.sellPropertiesFunc = sellPropertiesFunc
        self.noFunc = noFunc

        self.select = discord.ui.Select(placeholder="Sélectionnez les propriétés à vendre", min_values=1, max_values=10)

        for property in player.properties:
            self.select.add_option(label=f"{property.name} - {property.getSellPrice()}", value=property.position)

        self.add_item(self.select)


    @discord.ui.button(label="Vendre les propriétés sélectionnées", style=discord.ButtonStyle.green, row=2)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.sellPropertiesFunc(interaction, button, self.select.values)


    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.danger, row=2)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.noFunc(interaction, button)
