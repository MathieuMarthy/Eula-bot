import os

import discord
from discord.ext import commands, tasks

import data.config as config
from functions import Utils
from view.poll import pollView
from dao.pollDao import pollDao
# --- Setup ---
default_intents = discord.Intents.default().all()
default_intents.members = True
client: discord.Client = commands.Bot(command_prefix=config.prefix, help_command=None, intents=default_intents)
utils = Utils(client)
pollDao = pollDao()


@client.event
async def on_ready():
    # === general ===
    await load(os.path.join(utils.bot_path(), "commands"))

    synced = await client.tree.sync()
    print(f"{len(synced)} commandes synchronisées")

    print(f"Connecté à {client.user.name}")
    remove_tmp_files.start()

    # === guilds ===
    for guild in client.guilds:
        if not utils.server_exists_in_config(guild.id):
            utils.add_new_server(guild.id)

    # === polls ===
    print("Chargement des sondages...")
    await load_polls()


async def load(folder: str):
    """Load all the cogs"""

    for file in os.listdir(folder):
        file = os.path.join(folder, file)

        if os.path.isdir(file):
            await load(file)

        elif file.endswith(".py"):
            file = file.replace(utils.bot_path() + os.sep, "")
            file = file.replace("\\", ".").replace("/", ".").replace(":", ".")
            await client.load_extension(file[:-3])


async def load_polls():
    polls = pollDao.get_all_poll()

    for guild_id in polls:
        for channel_id in polls[guild_id]:
            for message_id in polls[guild_id][channel_id]:
                try:
                    channel = await client.fetch_channel(int(channel_id))
                    msg = await channel.fetch_message(int(message_id))
                except:
                    continue

                poll = utils.get_poll_object(int(guild_id), int(channel_id), int(message_id))
                await msg.edit(view=poll, embed=poll.embed)


@tasks.loop(minutes=1)
async def remove_tmp_files():
    """Remove all the files in tmp/"""
    for file in os.listdir("tmp"):
        os.remove(os.path.join("tmp", file))


client.run(config.token)
