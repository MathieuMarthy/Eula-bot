import discord
from discord.ui import View, Button


class ViewPagesView(View):
    
    def __init__(self, previous_func: callable,
                 next_func: callable,
                 timeout: int = 120,
                 buttons: list[discord.ui.Button] = None,
                 activeNavButton: bool = True
                 ) -> None:
        super().__init__(timeout=timeout)

        if buttons is not None:
            for button in buttons:
                self.add_item(button)

        # Nav buttons
        if not activeNavButton:
            return

        self.previous_func = previous_func
        self.next_func = next_func

        prevButton = Button(
            style=discord.ButtonStyle.secondary,
            custom_id="previous",
            emoji="⬅️")
        prevButton.callback = self.previous_func

        nextButton = Button(
            style=discord.ButtonStyle.secondary,
            custom_id="next",
            emoji="➡️")
        nextButton.callback = self.next_func

        self.add_item(prevButton)
        self.add_item(nextButton)
