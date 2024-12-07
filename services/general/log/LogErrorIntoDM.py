import traceback

import discord

from data import config

class LogErrorIntoDM:
    __instance = None

    @staticmethod
    def get_instance(client: discord.client):
        if LogErrorIntoDM.__instance is None:
            LogErrorIntoDM.__instance = LogErrorIntoDM(client)
        return LogErrorIntoDM.__instance
    
    
    def __init__(self, client: discord.Client):
        self.client = client
    
    
    async def log_error(self, exception: Exception):
        user = self.client.get_user(config.owner_id)
        date = discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        exception_details = traceback.format_exc()
        await user.send(f"{date}\n```{exception_details}```")
