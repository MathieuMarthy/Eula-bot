from typing import Tuple
import asyncio
import random

import discord
from uwutilities import String_tools
import yt_dlp

from models.music.playlistModel import PlaylistModel
from models.music.songModel import SongModel
from view.musicView import MusicView

embed_color = 0xf0a3ff

class MusicManager:
    vc: discord.VoiceClient
    queue: list[SongModel]
    current_song_msg: discord.Message
    channel: discord.TextChannel
    gl_id: int
    FFMPEG_OPTIONS: dict[str, str]

    def __init__(self, channel: discord.TextChannel) -> None:
        self.vc = None
        self.queue: list[SongModel] = []
        self.current_song_msg = None
        self.channel = channel
        self.gld_id = channel.guild.id

        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
        self.ydl = yt_dlp.YoutubeDL({
            "format": "bestaudio/best"
        })


    # == Functional == #
    # == Manage queue
    def add_to_queue(self, song: SongModel):
        self.queue.append(song)


    def next_song(self) -> SongModel:
        return self.queue.pop(0)


    def is_empty(self) -> bool:
        return len(self.queue) == 0


    def shuffle(self):
        random.shuffle(self.queue)


    # == Manage vc
    async def play_music_in_queue(self):
        if not self.is_empty() and not self.vc.is_playing():
            song = self.next_song()

            if self.current_song_msg is not None:
                await self.current_song_msg.delete()

            view = MusicView(
                self.toggle_play_pause,
                self.skip,
                self.stop,
                self.shuffle
            )
            self.current_song_msg = await self.channel.send(
                                            embed=self.get_msg_current_music(song),
                                            view=view)
            
            audio_source = discord.FFmpegPCMAudio(song.url, **self.FFMPEG_OPTIONS)
            self.vc.play(
                audio_source,
                after=lambda _: asyncio.run_coroutine_threadsafe(self.play_music_in_queue(), self.client.loop)
            )


    def search_yt(self, url: str, member: discord.Member):
        with self.ydl:
            try:
                info = self.ydl.extract_info(url, download=False)
            except Exception:
                return None

        return SongModel(info["title"], info["url"], info["duration"], info["thumbnail"], member)


    async def play(self, interaction: discord.Interaction, url: str):
        can_interact, message = await self._can_interact_with_me(interaction, False)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            self.suicide()
            return

        song = self.search_yt(url, interaction.user)
        if song is None:
            await interaction.response.send_message("Impossible de trouver la musique", ephemeral=True)
            self.suicide()
            return

        if self.vc is None:
            self.vc = await interaction.user.voice.channel.connect(self_deaf=True)

        elif self.vc.channel != interaction.user.voice.channel:
            self.move_to(interaction.user.voice.channel)

        self.add_to_queue(song)
        await interaction.response.send_message(embed=self.get_msg_add_queue(song))
        await self.play_music_in_queue()


    async def stop(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            self.suicide()
            return

        await self.vc.disconnect(force=True)
        del self.vc
        await interaction.response.send_message(embed=self.get_msg_stop())


    async def pause(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            self.suicide()
            return

        self.vc.pause()
        await interaction.response.send_message("Musique en pause", ephemeral=True)


    async def resume(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            self.suicide()
            return

        self.vc.resume()
        await interaction.response.send_message("Musique reprise", ephemeral=True)


    async def shuffle(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            self.suicide()
            return

        self.shuffle()
        await interaction.response.send_message("File d'attente mélangée", ephemeral=True)


    async def skip(self, interaction: discord.Interaction):
        can_interact, message = await self._can_interact_with_me(interaction, True)
        if not can_interact:
            await interaction.response.send_message(message, ephemeral=True)
            self.suicide()
            return

        self.vc.stop()
        await interaction.response.send_message("Musique suivante", ephemeral=True)


    async def toggle_play_pause(self, interaction: discord.Interaction):
        if self.vc.is_playing():
            self.vc.pause()
            await interaction.response.send_message("Musique en pause", ephemeral=True)
        else:
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


    def suicide(self):
        del self


    # == Messages == #
    def get_msg_add_queue(self, song: SongModel) -> discord.Embed:
        
        description = ""
        if isinstance(song, PlaylistModel):
            description += f"nombre de musiques: {len(song.songs)}"

        description += f"\# {len(self.queue)} dans la liste"

        return discord.Embed(
            title=f"{song.title} - {song.get_duration()}",
            url=song.url,
            description=description,
            color=embed_color
        )


    def get_msg_current_music(self, song: SongModel) -> discord.Embed:
        songs_left = len(self.queue)
        s_or_empty = String_tools.singular_or_plural(songs_left)

        embed = discord.Embed(
            title=song.title,
            url=song.url,
            description=f"Durée: {song.get_duration()} - {songs_left} musique{s_or_empty} restante{s_or_empty}",
            color=embed_color
        )
        embed.set_image(url=song.thumbnail)
        embed.set_footer(text=f"Ajoutée par {song.add_by.display_name}")
        return embed


    def get_msg_stop(self) -> discord.Embed:
        return discord.Embed(
            title="Musique arrêtée",
            color=embed_color
        )
