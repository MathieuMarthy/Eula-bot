import discord
from discord.ext import commands
from discord.ui import View

class WaitPlayerView(View):
    

    def __init__(self, funcJoin: callable, funcStart: callable, timeoutFunc: callable):
        super().__init__(timeout=120)
        self.timeoutFunc = timeoutFunc

        self.buttonJoin = discord.ui.Button(style=discord.ButtonStyle.primary, label="Rejoindre")
        self.buttonJoin.callback = funcJoin
        self.add_item(self.buttonJoin)

        self.buttonStart = discord.ui.Button(style=discord.ButtonStyle.green, label="Commencer")
        self.buttonStart.callback = funcStart
        self.add_item(self.buttonStart)


    async def on_timeout(self):
        await self.timeoutFunc()
