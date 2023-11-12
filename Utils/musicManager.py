import random

import discord
from uwutilities import String_tools

from models.music.playlistModel import PlaylistModel
from models.music.songModel import SongModel

embed_color = 0xf0a3ff

class MusicManager:
    vc: discord.VoiceClient
    queue: list[SongModel]
    current_song_msg: discord.Message

    def __init__(self, vc: discord.VoiceClient) -> None:
        self.vc = vc
        self.queue: list[SongModel] = []
        self.current_song_msg = None

    # == Functional == #
    def add_to_queue(self, song: SongModel):
        self.queue.append(song)


    def next_song(self) -> SongModel:
        return self.queue.pop(0)


    def is_empty(self) -> bool:
        return len(self.queue) == 0


    def shuffle(self):
        random.shuffle(self.queue)


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
