import asyncio
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class Timeout(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    async def command(self, ctx: commands.Context, member: discord.Member, duration: int, reason: str):
        if not ctx.guild.me.guild_permissions.moderate_members:
            await ctx.send("Je n'ai pas les permissions de timeout")
            return

        if member.guild_permissions.administrator:
            await ctx.send("Impossible de timeout un administrateur")
            return

        kamehameha_emotes = [
            ("<:k1:1031645200851939328>", "<:k0:1031645223580876864>"),
            ("<:k2:1031645202475143188>", "<:k0:1031645223580876864>"),
            ("<:k3:1031645203397869630>", "<:k0:1031645223580876864>"),
            ("<:k4:1031645205302083604>", "<:k0:1031645223580876864>"),
            ("<:k5a:1031645206593945702>", "<:k5b:1031645208112279582>"),
            ("<:k6a:1031645209404117012>", "<:k6b:1031645210779861063>"),
            ("<:k7a:1031645212352712854>", "<:k7b:1031645213652946976>"),
            ("<:k8a:1031645215355838587>", "<:k8b:1031645216828043325>"),
            ("<:k9a:1031645218879045783>", "<:k9b:1031645220640657489>"),
            ("<:k10a:1031645221861199913>", "<:k0:1031645223580876864>"),
        ]

        delta = timedelta(minutes=duration)
        await member.timeout(delta, reason=reason)

        msg = await ctx.send("".join(kamehameha_emotes[0]))
        for emotes in kamehameha_emotes:
            await msg.edit(content=f"{emotes[0]}{emotes[1]}{member.mention}")
            await asyncio.sleep(1)

        await msg.edit(content=f"{member.mention} a été timeout pendant {duration} minute{'s' if duration > 1 else ''}{' pour ' + reason if reason else ''}")


    @commands.command(aliases=["to"])
    async def timeout(self, ctx: commands.Context, member: str, duration: str, reason: str = ""):
        if not duration.isdigit():
            await ctx.send("La duree doit être un nombre")

        member = self.utils.get_member(member)
        if member is None:
            await ctx.send("Utilisateur introuvable")
            return

        await self.command(ctx, member, int(duration), reason)


    @app_commands.command(name="timeout", description="ADMIN, timeout une personne pendant une durée")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(personne="La personne à timeout")
    @app_commands.describe(duree="La durée du timeout en minutes")
    @app_commands.describe(raison="La raison du timeout, optionnel")
    async def timeoutSlash(self, interaction: discord.Interaction, personne: discord.Member, duree: int, raison: str = ""):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, personne, duree, raison)


    @timeout.error
    async def timeoutError(self, ctx, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await ctx.send(error_string)
        else:
            raise error


    @timeoutSlash.error
    async def timeoutSlashError(self, interaction, error):
        error_string = self.utils.error_message(error)
        if error_string is not None:
            await interaction.response.send_message(error_string, ephemeral=True)
        else:
            raise error



async def setup(bot):
    await bot.add_cog(Timeout(bot))
