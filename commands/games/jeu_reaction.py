from requests import get as get_request
from random import randint
import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from functions import Utils

class TenFastFingers(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.utils = Utils(client)


    async def command(self, ctx, nb_manches):
        list_user, dico_points = await self.utils.start_game_multi(ctx, nb_manches, "10fastfinger")
        if not list_user:
            return

        turn = 0

        def get_sentences():
            a = get_request("https://enneagon.org/phrases").text

            start = a.find('<p id="phr">')
            a = a[start + 12: a.find("</div>", start) - 6]
            a = self.utils.replaces(a, "&nbsp", "", ";", "", " <br>", "")
            for e in a:
                e = e.replace("É", "E")

            return [i.strip() for e in a.split(".") for i in e.split(",") if 70 > len(i) > 20]

        list_question = get_sentences()
        while turn != nb_manches:

            mot = list_question[randint(0, len(list_question) - 1)]
            embed = discord.Embed(color=0xf0a3ff)
            embed.add_field(name="Phrase", value=mot, inline=False)
            await ctx.send(embed=embed)
            list_question.remove(mot)

            if len(list_question) == 0:
                list_question = get_sentences()
            try:
                msg = await self.client.wait_for("message",
                    check=lambda message: message.author in list_user and message.content in [mot,
                        "exit",
                        "!exit",
                        "leave",
                        "!leave",
                        "Exit",
                        "!Exit",
                        "leave",
                        "Leave"],
                    timeout=60) 
            except asyncio.TimeoutError:
                await ctx.send("partie finie à cause d'inactivité")
                break

            if msg.content.lower() in ["exit", "!exit", "leave", "!leave"]:
                await ctx.send("partie annulée !")
                return
            dico_points[msg.author.id] += 1
            await ctx.send(f"**{msg.author}** gagne le point ! {dico_points[msg.author.id]} points")
            turn += 1
            await asyncio.sleep(3)

        await self.utils.end_game(ctx, list_user, dico_points)


    @commands.command(aliases=["10ff", "10fastfingers", "10_fast_fingers"])
    async def tenfastfingers(self, ctx, nb_manches: str = "5"):
        nb_manches = int(nb_manches) if nb_manches.isdigit() else 5
        await self.command(ctx, nb_manches)


    @app_commands.command(name="10_fast_fingers", description="multijoueur: dans ce jeu, vous devez taper le plus de mots possible")
    @app_commands.describe(nb_manches="nombre de manches, par défaut 5")
    async def tenfastfingersSlash(self, interaction: discord.Interaction, nb_manches: int = 5):
        ctx = await commands.Context.from_interaction(interaction)
        await self.command(ctx, nb_manches)


async def setup(bot):
    await bot.add_cog(TenFastFingers(bot))
