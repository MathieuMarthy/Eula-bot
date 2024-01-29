from typing import Optional, Tuple, Any, Callable

import discord

from models.riot.memberRankLol import MemberRankLol
from services.general.viewPages.viewPagesView import ViewPagesView


class ViewPages:

    def __init__(self,
                 interaction: discord.Interaction,
                 title: str,
                 collection: list,
                 nb_per_pages: int,
                 item_to_str: callable,
                 ephemeral: bool = False,
                 buttons_and_callback: Optional[list[Tuple[discord.ui.Button, Callable[[int, list[Any]], list[MemberRankLol]]]]] = None
                 ) -> None:

        buttons = []
        if buttons_and_callback is not None:
            for button, callback in buttons_and_callback:
                button.callback = lambda inte: self._custom_callback(self.interaction.guild_id, callback, inte)
                buttons.append(button)

        activeNavButton = buttons_and_callback is None or len(buttons_and_callback) not in [0, 1]
        self.view = ViewPagesView(self._previous_page, self._next_page, buttons=buttons,
                                  activeNavButton=activeNavButton)
        self.current_page = 0

        self.interaction = interaction
        self.title = title
        self.collection = collection
        self.nb_per_pages = nb_per_pages
        self.item_to_str = item_to_str
        self.ephemeral = ephemeral

    async def _custom_callback(self,
                               guildId: int,
                               callback: Callable[[int, list[Any]], list[MemberRankLol]],
                               inte: discord.Interaction):
        try:
            await inte.response.defer(ephemeral=True, thinking=True)
            updated_items = callback(guildId, self._get_page(self.current_page))
            self._update_current_items(updated_items)
            await self._update_msg()
            await inte.followup.send("Les données de cette page ont été mises à jour", ephemeral=True)
        except Exception as e:
            await self._send_ephemeral_message(f"Une erreur est survenue:\n{e}")

    async def _send_ephemeral_message(self, content: str):
        await self.interaction.followup.send(content=content, ephemeral=True)

    async def start(self):
        if len(self.collection) == 0:
            embed = discord.Embed(
                title=self.title,
                description="Aucun élément à afficher",
                color=0x989eec
            )
            await self.interaction.response.send_message(
                embed=embed,
                ephemeral=self.ephemeral
            )
            return

        if self._get_total_pages() == 1:
            await self.interaction.response.send_message(
                embed=self._get_embed(),
                ephemeral=self.ephemeral,
                view=self.view
            )
            return

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

    async def _update_msg(self):
        await self.interaction.edit_original_response(embed=self._get_embed())

    def _update_current_items(self, items: list[Any]):

        start = self.current_page * self.nb_per_pages
        end = (self.current_page + 1) * self.nb_per_pages
        self.collection[start:end] = items

    async def _next_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.current_page < self._get_total_pages() - 1:
            self.current_page += 1
        else:
            self.current_page = 0

        await self._update_msg()

    async def _previous_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.current_page > 0:
            self.current_page -= 1
        else:
            self.current_page = self._get_total_pages() - 1

        await self._update_msg()

    def _get_total_pages(self):
        return -(-len(self.collection) // self.nb_per_pages)

    def _get_page(self, page_number):
        start = page_number * self.nb_per_pages
        end = (page_number + 1) * self.nb_per_pages
        return self.collection[start:end]
