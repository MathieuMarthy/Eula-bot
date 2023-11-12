import discord
from discord.ui import View

class MusicView(View):

    def __init__(
            self,
            toggle_play_pause: callable,
            skip: callable,
            stop: callable,
            shuffle: callable
        ):
        super().__init__(timeout=None)
        self.toggle_play_pause = toggle_play_pause
        self.skip = skip
        self.stop = stop
        self.shuffle = shuffle


    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.green)
    async def toggle_play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_play_pause(interaction)


    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.green)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.skip(interaction)


    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.green)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.stop(interaction)


    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.green)
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.shuffle(interaction)
