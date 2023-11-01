import discord
from discord.ext import commands

from view.waitPlayerView import WaitPlayerView

class WaitPlayer:
    players: list[discord.Member]
    owner: discord.Member
    func: callable
    ctx: commands.Context
    msg: discord.Message
    maxPlayer: int
    view: WaitPlayerView

    def __init__(self, title: str, ctx: commands.Context, owner: discord.Member, funcToCall: callable, maxPlayer: int = None) -> None:
        self.players: list[discord.Member] = [owner]
        self.title = title
        self.owner = owner
        self.func = funcToCall
        self.ctx = ctx
        self.msg = None
        self.maxPlayer = maxPlayer
        self.view = WaitPlayerView(self._callbackAddPlayer, self._callbackStartFunc)


    async def start(self):
        self.msg = await self.ctx.send(embed=self._getEmbed(), view=self.view)
    

    async def _editMsg(self):
        await self.msg.edit(embed=self._getEmbed())


    def _getEmbed(self):
        embed = discord.Embed(title=self.title, color=0x989eec)
        embed.add_field(name="Joueurs", value=", ".join([player.mention for player in self.players]), inline=True)
        return embed


    async def _callbackAddPlayer(self, interaction: discord.Interaction):
        user = interaction.user

        if len(self.players) >= self.maxPlayer:
            await interaction.response.send_message("La partie est déjà pleine", ephemeral=True)
            return

        if user in self.players:
            await interaction.response.send_message("Vous êtes déjà dans la partie", ephemeral=True)
            return

        self.players.append(interaction.user)
        await interaction.response.defer()
        await self.msg.edit(embed=self._getEmbed())


    async def _callbackStartFunc(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("Seul le créateur de la partie peut la lancer", ephemeral=True)
            return
        
        await interaction.response.defer()
        await self.func(self.ctx, self.players)
