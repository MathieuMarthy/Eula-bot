from datetime import timedelta

import discord

class SongModel:
    title: str
    url: str
    duration: int
    playlist: bool
    thumbnail: str
    add_by: discord.Member


    def __init__(self, title: str, url: str, duration: int, thumbnail: str, add_by: discord.Member) -> None:
        self.title = title
        self.url = url
        self.duration = duration
        self.thumbnail = thumbnail
        self.add_by = add_by


    def get_duration(self) -> str:
        time_str = str(timedelta(seconds=self.duration))

        if time_str.startswith("0:"):
            return time_str[2:]
        return time_str
