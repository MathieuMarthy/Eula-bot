from datetime import timedelta

import discord

class SongModel:
    title: str
    url: str
    duration: int
    playlist: bool
    add_by: discord.Member

    def __init__(self, title: str, url: str, duration: int, add_by: discord.Member) -> None:
        self.title = title
        self.url = url
        self.duration = duration
        self.add_by = add_by

    def get_duration(self) -> str:
        return str(timedelta(seconds=self.duration))
