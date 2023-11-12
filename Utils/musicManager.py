
import discord
from models.music.playlistModel import PlaylistModel
from models.music.songModel import SongModel

embed_color = 0xf0a3ff

class MusicManager:
    vc: discord.VoiceClient
    queue: list[SongModel]

    def __init__(self, vc: discord.VoiceClient) -> None:
        self.vc = vc
        self.queue: list[SongModel] = []
    
    # == Functional == #
    def add_to_queue(self, song: SongModel):
        self.queue.append(song)


    def next_song(self) -> SongModel:
        return self.queue.pop(0)


    def is_empty(self) -> bool:
        return len(self.queue) == 0


    # == Messages == #
    def msg_add_queue(self, song: SongModel) -> discord.Embed:
        description = f"Durée: {song.get_duration()}"
        
        if isinstance(song, PlaylistModel):
            description += f"nombre de musiques: {len(song.songs)}"

        description += f"\nAjoutée par {song.add_by.mention}"

        return discord.Embed(
            title=song.title,
            url=song.url,
            description=description,
            color=embed_color
        )


    def msg_current_music(self, song: SongModel) -> discord.Embed:
        return discord.Embed(
            title=song.title,
            url=song.url,
            description=f"Durée: {song.get_duration()}",
            color=embed_color
        )
