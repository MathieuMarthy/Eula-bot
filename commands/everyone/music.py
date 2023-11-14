import discord
from discord import app_commands
from discord.ext import commands

from Utils.musicManager import MusicManager


class Music(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.music_managers: list[MusicManager] = []

    
    def _get_music_manger(self, interaction: discord.Interaction) -> MusicManager:
        for music_manager in self.music_managers:
            if music_manager.gld_id == interaction.guild_id:
                return music_manager

        music_manager = MusicManager(self.client, interaction.channel)
        self.music_managers.append(music_manager)
        return music_manager


    @app_commands.command(name="play", description="joue une musique")
    @app_commands.describe(url="url youtube de la musique")
    async def play(self, interaction: discord.Interaction, url: str):
        musicManager = self._get_music_manger(interaction)
        await musicManager.play(interaction, url)


    @app_commands.command(name="stop", description="stop la musique")
    async def stop(self, interaction: discord.Interaction):
        musicManager = self._get_music_manger(interaction)
        await musicManager.stop(interaction)
        del musicManager


    @app_commands.command(name="pause", description="pause la musique")
    async def pause(self, interaction: discord.Interaction):
        MusicManager = self._get_music_manger(interaction)
        await MusicManager.pause(interaction)


    @app_commands.command(name="resume", description="reprend la musique")
    async def resume(self, interaction: discord.Interaction):
        MusicManager = self._get_music_manger(interaction)
        await MusicManager.resume(interaction)


    @app_commands.command(name="shuffle", description="mélange la file d'attente")
    async def shuffle(self, interaction: discord.Interaction):
        MusicManager = self._get_music_manger(interaction)
        await MusicManager.shuffle(interaction)


    @app_commands.command(name="skip", description="passe à la musique suivante")
    async def skip(self, interaction: discord.Interaction):
        MusicManager = self._get_music_manger(interaction)
        await MusicManager.skip(interaction)


async def setup(bot):
    await bot.add_cog(Music(bot))
