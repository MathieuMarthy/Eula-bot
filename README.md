
<p align="center">
    <img src="./documentation/decoration.png" alt="" height="200" />
</p>

<h1 align="center">Eula Bot</h1>
<h3 align="center">Fun, Moderation and Utilities</h3>

<p  align="center">
    <a href="https://discord.com/api/oauth2/authorize?client_id=914226393565499412&permissions=8&scope=applications.commands%20bot">
        <img src="./documentation/invite-Eula.png" alt="invite Eula-bot" width="150">
    </a>
</p>
<br>

## Presentation
Eula is a Discord bot designed to help you with your server. It can moderate your server, entertain you, and assist you in your daily tasks.

If you have suggestions or find bugs, contact me @kojhyy.

<br>

## Installation

### Use the docker image

You can use the docker image attached to this repo

Pull the image
```bash
docker pull ghcr.io/mathieumarthy/eula-bot:latest
```

The first time you run the container, you need to set the environment variables
```bash
docker run -d --name eula-bot \
  -e token="YOUR_DISCORD_BOT_TOKEN" \
  -e reddit_id="YOUR_REDDIT_APP_ID" \
  -e reddit_secret="YOUR_REDDIT_APP_SECRET" \
  -e riot_api_key="YOUR_RIOT_API_KEY" \
  ghcr.io/mathieumarthy/eula-bot:latest
```

### Or clone the repo and setup python

Clone the repo
```bash
git clone https://github.com/MathieuMarthy/Eula-bot.git
```

Create a venv and install requirements
```bash
python3 -m venv ./venv
source .venv/bin/activate
pip install -r requirements.txt
```

run the project
```bash
python3 main.py
```
<br>

## All Commands

### 👑 Admin
- `send`: Sends a message to a channel.
- `send_embed`: Sends an embed to a channel.
- `help_send_embed`: Sends a help message for the send_embed command.
- `clear`: Deletes a number of messages or up to a given message.
- `nuke`: Deletes a channel and recreates it with the same settings.
- `reaction`: Adds reactions to a message.
- `timeout`: Times out a person for a duration.
- `sondage`: Creates a poll with up to 5 choices.
- `toggle_autorole`: Enables or disables role assignment when joining the server.
- `toggle_logs`: Enables or disables logs.
- `toggle_logs_voice`: Enables or disables role assignment when a user joins a voice channel.
- `toggle_welcome_message`: Enables or disables the welcome message in DM.

### 💬 Chat
- `bonjour`: Say hello to someone!
- `mord`: Bite someone!
- `bisous`: Give someone a kiss!
- `tapoter`: *pat pat*
- `calin`: 🤗
- `baka`: Ba...baka!

### 🔧 Utility
- `pp`: Sends someone's profile picture
- `bannière`: Sends someone's banner
- `ping`: Ping the bot
- `choisis`: Choose between multiple options (separated by commas)
- `help`: Interactive help menu
- `rappel`: Create a reminder (format: dd/mm/yyyy hh:mm)

### 🌍 General
- `reddit`: Sends images from a subreddit
- `8ball`: The magic 8-ball answers your questions
- `pile_ou_face`: Heads or tails
- `randomizer_lol`: Gives a random champion, items and runes
- `image_sfw`: Sends a random anime image
- `add_lol_account`: Registers a LoL account on the server
- `remove_lol_account`: Removes a LoL account from the server
- `show_lol_rank`: Shows a user's LoL accounts
- `lol_leaderboard`: Shows the LoL player leaderboard for the server
- `lol_ranked_history`: Shows the last 10 ranked games

### 🎮 Games
- `10_fast_fingers`: Multiplayer: in this game, you must type as many words as possible
- `monopoly`: Multiplayer: monopoly game with custom rules, items, ...
