import os

import discord
from discord import app_commands
from discord.ext import commands, tasks

import config

# --- Setup ---
default_intents = discord.Intents.default().all()
default_intents.members = True
client: discord.Client = commands.Bot(command_prefix=config.prefix, help_command=None, intents=default_intents)


@client.event
async def on_ready():

    await load("commands")

    synced = await client.tree.sync()
    print(f"{len(synced)} commandes synchronisées")

    print(f"Connecté à {client.user.name}")
    remove_tmp_files.start()


async def load(folder: str):
    """Load all the cogs"""

    for file in os.listdir(folder):
        file = os.path.join(folder, file)

        if os.path.isdir(file):
            await load(file)

        elif file.endswith(".py"):
            file = file.replace("\\", ".").replace("/", ".")
            await client.load_extension(file[:-3])


@tasks.loop(minutes=1)
async def remove_tmp_files():
    """Remove all the files in tmp/"""
    os.system(f"del /f /q \"{os.path.join(config.path, 'tmp', '*.*')}\"")


client.run(config.token)
