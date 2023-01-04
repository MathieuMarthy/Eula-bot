import os

import discord
from discord.ext import commands

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


async def load(folder: str):
    """Load all the cogs"""

    for file in os.listdir(folder):
        file = os.path.join(folder, file)

        if os.path.isdir(file):
            await load(file)

        elif file.endswith(".py"):
            file = file.replace("\\", ".").replace("/", ".")
            await client.load_extension(file[:-3])


client.run(config.token)
