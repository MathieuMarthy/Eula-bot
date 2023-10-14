import discord
from discord.ui import View, Select


class BoardView(View):
    def __init__(self):
        super().__init__(timeout=None)

    