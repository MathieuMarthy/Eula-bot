from typing import Tuple
import asyncio

import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp

from models.musicModel import MusicModel


class Music(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

        self.ydl = yt_dlp.YoutubeDL({
            "format": "bestaudio/best"
        })

        self.queue: list[MusicModel] = []
        self.is_playing = False
        self.is_paused = False
        self.vc = None

        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}


    def search_yt(self, url: str):
        with self.ydl:
            try:
                info = self.ydl.extract_info(url, download=False)
            except Exception:
                return None

        return MusicModel(info["title"], info["url"], info["duration"])
    

    async def play_music_in_queue(self):
        if len(self.queue) > 0:
            self.is_playing = True

            song = self.queue[0]
            self.queue.pop(0)

            audio_source = discord.FFmpegPCMAudio(song.url, **self.FFMPEG_OPTIONS, executable=r"C:\Program Files\ffmpeg\bin\ffmpeg.exe")
            self.vc.play(audio_source, after=lambda _: self.play_music_in_queue())
        else:
            self.is_playing = False


    @app_commands.command(name="play", description="joue une musique")
    @app_commands.describe(url="url youtube de la musique")
    async def playSlash(self, interaction: discord.Interaction, url: str):
        can_interact, message = await self._can_interact_with_me(interaction, False)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            return

        song = self.search_yt(url)
        if song is None:
            await interaction.response.send_message("Impossible de trouver la musique", ephemeral=True)
            return

        if self.vc is None:
            self.vc = await interaction.user.voice.channel.connect(self_deaf=True)

        elif self.vc.channel != interaction.user.voice.channel:
            self.vc.move_to(interaction.user.voice.channel)

        self.queue.append(song)
        await interaction.response.send_message(f"Musique ajoutée à la queue: {song.title}", ephemeral=True)
        await self.play_music_in_queue()


    @app_commands.command(name="stop", description="stop la musique")
    async def stopSlash(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            return

        await self.vc.disconnect(force=True)
        self.vc = None
        self.is_playing = False
        await interaction.response.send_message("Musique stoppée", ephemeral=True)


    @app_commands.command(name="pause", description="pause la musique")
    async def pauseSlash(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            return

        self.is_paused = True
        self.vc.pause()
        await interaction.response.send_message("Musique en pause", ephemeral=True)
    

    @app_commands.command(name="resume", description="reprend la musique")
    async def resumeSlash(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            return

        self.is_paused = False
        self.vc.resume()
        await interaction.response.send_message("Musique reprise", ephemeral=True)


    async def _can_interact_with_me(self, interaction: discord.Interaction, i_need_to_be_same_vc: bool) -> Tuple[bool, str]:
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            return False, "Vous devez être dans un salon vocal pour utiliser cette commande"

        elif i_need_to_be_same_vc and not self.vc:
            return False, "Je ne suis pas dans un salon vocal"

        elif i_need_to_be_same_vc and interaction.user.voice.channel != self.vc.channel:
            return False, "Vous devez être dans le même salon vocal que moi pour utiliser cette commande"

        return True, ""


async def setup(bot):
    await bot.add_cog(Music(bot))
