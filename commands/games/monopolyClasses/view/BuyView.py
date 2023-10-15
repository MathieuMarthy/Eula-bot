import discord
from discord.ui import View


class BuyView(View):
    
    def __init__(self, buy_func: callable, no_func: callable):
        super().__init__(timeout=None)
        self.buy_func = buy_func
        self.no_func = no_func


    @discord.ui.button(label="Acheter la case", custom_id="buy", style=discord.ButtonStyle.green)
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.buy_func(interaction, button)


    @discord.ui.button(label="Ne pas acheter", custom_id="no", style=discord.ButtonStyle.red)
    async def nobuy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.no_func(interaction, button)
