from models.music.songModel import SongModel


class PlaylistModel(SongModel):
    songs: list[SongModel]

    def __init__(self, title: str, url: str, songs: list[SongModel]) -> None:
        self.songs: list[SongModel] = songs
        duration = sum([song.duration for song in songs])
        super().__init__(title, url, duration)
