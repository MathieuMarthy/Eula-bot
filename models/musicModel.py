import discord

class MusicModel:
    title: str
    url: str
    duration: int

    def __init__(self, title: str, url: str, duration: int) -> None:
        self.title = title
        self.url = url
        self.duration = duration
