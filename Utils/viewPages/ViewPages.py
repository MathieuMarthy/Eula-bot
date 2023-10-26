from math import ceil
import discord

from Utils.viewPages.viewPagesView import ViewPagesView


class View_pages:

    def __init__(self, interaction: discord.Interaction, title: str, collection: list, nb_per_pages: int, item_to_str: callable, ephemeral: bool = False) -> None:
        self.view = ViewPagesView(self._previous_page, self._next_page)
        self.current_page = 0
        
        self.interaction = interaction
        self.title = title
        self.collection = collection
        self.nb_per_pages = nb_per_pages
        self.item_to_str = item_to_str
        self.ephemeral = ephemeral

    
    async def start(self):
        await self.interaction.response.send_message(
            embed=self._get_embed(),
            view=self.view,
            ephemeral=self.ephemeral
        )


    def _get_embed(self) -> discord.Embed:
        embed = discord.Embed(title=self.title, description=self._get_description(), color=0x989eec)
        embed.set_footer(text=self._get_footer())
        return embed


    def _get_description(self) -> str:
        return "\n".join([self.item_to_str(item) for item in self._get_page(self.current_page)])


    def _get_footer(self) -> str:
        return f"Page {self.current_page + 1}/{self._get_total_pages()}"

    
    async def _update(self):
        await self.interaction.edit_original_response(embed=self._get_embed())


    async def _next_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.current_page < self._get_total_pages() - 1:
            self.current_page += 1
        else:
            self.current_page = 0
        
        await self._update()


    async def _previous_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.current_page > 0:
            self.current_page -= 1
        else:
            self.current_page = self._get_total_pages() - 1
        
        await self._update()


    def _get_total_pages(self):
        return -(-len(self.collection) // self.nb_per_pages)


    def _get_page(self, page_number):
        start = page_number * self.nb_per_pages
        end = (page_number + 1) * self.nb_per_pages
        return self.collection[start:end]
