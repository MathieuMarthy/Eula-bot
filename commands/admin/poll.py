from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
from dao.pollDao import pollDao

from functions import Utils
from view.poll import pollView

class Poll(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils.get_instance(client)
        self.pollDao = pollDao.get_instance()

    async def command(
            self,
            ctx: commands.Context,
            channel: discord.TextChannel,
            duration: str,
            question: str,
            choix1, choix2, choix3, choix4, choix5
            ):
        tous_choix = [choix1, choix2, choix3, choix4, choix5]
        tous_choix = [choix for choix in tous_choix if choix is not None]

        end_time: datetime = self.utils.string_duration_to_datetime(duration)
        end_timestamp = round(end_time.timestamp())

        # check if 2 choices are the same
        for choix in tous_choix:
            if tous_choix.count(choix) > 1:
                await ctx.send(f"Vous ne pouvez pas avoir 2 choix identiques\n{choix} est présent {tous_choix.count(choix)} fois")
                return

        msg = await channel.send("Sondage en chargement...")


        self.pollDao.create_poll(channel.guild.id, channel.id, msg.id, end_timestamp, question, tous_choix)
        view = pollView(ctx.guild.id, channel.id, msg.id, end_timestamp, question, tous_choix)

        await msg.edit(content="", view=view, embed=view.embed)
        if ctx.interaction is not None:
            await ctx.interaction.response.send_message(f"Le sondage a été envoyé dans le salon {channel.mention}", ephemeral=True)
        else:
            await ctx.send(f"Le sondage a été envoyé dans le salon {channel.mention}")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sondage(self, ctx: commands.Context, channel: discord.TextChannel, duree: str, question: str, choix1: str, choix2: str, choix3: str = None, choix4: str = None, choix5: str = None):

        channel = channel.replace("<", "").replace("#", "").replace(">", "")
        channel = ctx.guild.get_channel(int(channel))

        if channel is None:
            await ctx.send("Le salon est invalide")
            return

        await self.command(ctx, channel, duree, question, choix1, choix2, choix3, choix4, choix5)


    @app_commands.command(name="sondage", description="créer un sondage")
    @commands.has_permissions(administrator=True)
    @app_commands.describe(channel="le channel où le sondage sera envoyé")
    @app_commands.describe(duree="la durée du sondage. (ex: 1 an 2 mois 3 jours 4 heures 5 minutes 6 secondes)")
    @app_commands.describe(question="la question du sondage")
    @app_commands.describe(choix1="choix1")
    @app_commands.describe(choix2="choix2")
    @app_commands.describe(choix3="choix3")
    @app_commands.describe(choix4="choix4")
    @app_commands.describe(choix5="choix5")
    async def sondageSlash(self, interaction: discord.Interaction, channel: discord.TextChannel, duree: str, question: str, choix1: str, choix2: str, choix3: str = None, choix4: str = None, choix5: str = None):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, channel, duree, question, choix1, choix2, choix3, choix4, choix5)


async def setup(bot):
    await bot.add_cog(Poll(bot))
