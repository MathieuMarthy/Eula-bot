import os

import discord
from discord.ext import commands, tasks

import data.config as config
from functions import Utils
# --- Setup ---
default_intents = discord.Intents.default().all()
default_intents.members = True
client: discord.Client = commands.Bot(command_prefix=config.prefix, help_command=None, intents=default_intents)
utils = Utils(client)


@client.event
async def on_ready():
    # === general ===
    await load("commands")

    synced = await client.tree.sync()
    print(f"{len(synced)} commandes synchronisées")

    print(f"Connecté à {client.user.name}")
    remove_tmp_files.start()

    # === guilds ===
    for guild in client.guilds:
        if not utils.server_exists_in_config(guild.id):
            utils.add_new_server(guild.id)


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
    for file in os.listdir("tmp"):
        os.remove(os.path.join("tmp", file))


client.run(config.token)
