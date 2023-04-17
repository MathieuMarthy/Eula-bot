import discord
from discord.ui import View, Select
from discord.ext import commands

from dao.pollDao import pollDao

class pollView(View):
    def __init__(self, client, guild_id: int, channel_id: int, message_id, question: str, choix: list):
        super().__init__(timeout=None)
        self.pollDao = pollDao()
        self.question = question
        self.choix = choix
        self.infos = (guild_id, channel_id, message_id)

        options = [
            discord.SelectOption(label=key, value=key)
            for key in self.choix
        ]
        
        select = Select(placeholder="Choisissez une option", options=options)
        select.callback = self.select_callback
        self.add_item(select)

        self.embed = self.create_embed(self.calculate_results())

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        value_selected = interaction.data["values"][0]
        value_selected_index = self.choix.index(value_selected)

        self.pollDao.add_member_poll(self.infos[0], self.infos[1], self.infos[2], interaction.user.id, value_selected_index)

        self.embed = self.create_embed(self.calculate_results())
        await interaction.message.edit(embed=self.embed, view=self)


    def calculate_results(self):
        """
        results synxtax:
        (numbers of votes, pourcentage)
            [(5, 50), (2, 20), (3, 30)]
        """

        poll_json = self.pollDao.get_vote_poll(self.infos[0], self.infos[1], self.infos[2])
        # josn syntax:
        # {
        #    member_id: choix_index
        # }

        results = [0] * len(self.choix)

        for _, choix_index in poll_json.items():
            results[choix_index] += 1

        total_votes = sum(results)

        if total_votes == 0:
            return [(0, 0)] * len(self.choix)

        results = [(result, round(result / total_votes * 100)) for result in results]
        return results


    def create_embed(self, results: list):
        description = "\n".join([f"**{i + 1}.** {choix}\n{self.create_bar(results[i][1])} {results[i][0]} votes - {results[i][1]}%" for i, choix in enumerate(self.choix)])

        embed = discord.Embed(
            title=self.question,
            description=description,
            color=0x989eec
        )

        return embed

    def create_bar(self, pourcentage: int):
        pourcentage //= 10
        bar = "⬛" * pourcentage
        bar += "⬜" * (10 - pourcentage)
        return bar
