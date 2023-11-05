import discord
from discord.ui import View


class PopupView(View):
    
    def __init__(self, yes_func: callable, no_func: callable):
        super().__init__(timeout=None)
        self.yes_func = yes_func
        self.no_func = no_func


    @discord.ui.button(label="Oui", custom_id="yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.yes_func(interaction)


    @discord.ui.button(label="Non", custom_id="no", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.no_func(interaction, "...")
