import asyncio
from typing import Tuple

import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp

from Utils.musicManager import MusicManager
from models.music.songModel import SongModel


class Music(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

        self.ydl = yt_dlp.YoutubeDL({
            "format": "bestaudio/best"
        })

        self.music_manager: dict[int, MusicManager] = {}
        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}


    def search_yt(self, url: str, member: discord.Member):
        with self.ydl:
            try:
                info = self.ydl.extract_info(url, download=False)
            except Exception:
                return None

        return SongModel(info["title"], info["url"], info["duration"], info["thumbnail"], member)
    

    async def play_music_in_queue(self, interaction: discord.Interaction):
        
        gl_id = interaction.guild_id
        if not self.music_manager[gl_id].is_empty() and not self.music_manager[gl_id].vc.is_playing():
            song = self.music_manager[gl_id].next_song()

            if self.music_manager[gl_id].current_song_msg is not None:
                await self.music_manager[gl_id].current_song_msg.delete()

            self.music_manager[gl_id].current_song_msg = await interaction.channel.send(embed=self.music_manager[gl_id].get_msg_current_music(song))
            
            audio_source = discord.FFmpegPCMAudio(song.url, **self.FFMPEG_OPTIONS)

            self.music_manager[gl_id].vc.play(
                audio_source,
                after=lambda _: asyncio.run_coroutine_threadsafe(self.play_music_in_queue(interaction), self.client.loop)
            )
 

    @app_commands.command(name="play", description="joue une musique")
    @app_commands.describe(url="url youtube de la musique")
    async def playSlash(self, interaction: discord.Interaction, url: str):
        can_interact, message = await self._can_interact_with_me(interaction, False)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            return

        song = self.search_yt(url, interaction.user)
        if song is None:
            await interaction.response.send_message("Impossible de trouver la musique", ephemeral=True)
            return

        gd_id = interaction.guild_id
        if self.music_manager.get(gd_id, None) is None:
            self.music_manager[gd_id] = MusicManager(None)

        if self.music_manager[gd_id].vc is None:
            self.music_manager[gd_id].vc = await interaction.user.voice.channel.connect(self_deaf=True)

        elif self.music_manager[gd_id].vc.channel != interaction.user.voice.channel:
            self.music_manager[gd_id].move_to(interaction.user.voice.channel)

        self.music_manager[gd_id].add_to_queue(song)
        await interaction.response.send_message(embed=self.music_manager[gd_id].get_msg_add_queue(song))
        await self.play_music_in_queue(interaction)


    @app_commands.command(name="stop", description="stop la musique")
    async def stopSlash(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            return

        gd_id = interaction.guild_id
        await self.music_manager[gd_id].vc.disconnect(force=True)
        del self.music_manager[gd_id].vc
        await interaction.response.send_message(embed=self.music_manager[gd_id].get_msg_stop())


    @app_commands.command(name="pause", description="pause la musique")
    async def pauseSlash(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            return

        self.music_manager[interaction.guild_id].vc.pause()
        await interaction.response.send_message("Musique en pause", ephemeral=True)


    @app_commands.command(name="resume", description="reprend la musique")
    async def resumeSlash(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            return

        self.music_manager[interaction.guild_id].vc.resume()
        await interaction.response.send_message("Musique reprise", ephemeral=True)
    

    @app_commands.command(name="shuffle", description="mélange la file d'attente")
    async def shuffleSlash(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            return

        self.music_manager[interaction.guild_id].shuffle()
        await interaction.response.send_message("File d'attente mélangée", ephemeral=True)


    async def _can_interact_with_me(self, interaction: discord.Interaction, i_need_to_be_same_vc: bool) -> Tuple[bool, str]:
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            return False, "Vous devez être dans un salon vocal pour utiliser cette commande"

        elif i_need_to_be_same_vc and not self.music_manager[interaction.guild_id].vc:
            return False, "Je ne suis pas dans un salon vocal"

        elif i_need_to_be_same_vc and interaction.user.voice.channel != self.music_manager[interaction.guild_id].vc.channel:
            return False, "Vous devez être dans le même salon vocal que moi pour utiliser cette commande"

        return True, ""


async def setup(bot):
    await bot.add_cog(Music(bot))
