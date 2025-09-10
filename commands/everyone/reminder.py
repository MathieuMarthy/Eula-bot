from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from dao.reminderDao import ReminderDao
from data import config
from models.reminderModel import ReminderModel

class Reminder(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.reminder = ReminderDao.get_instance()


    @app_commands.command(name="rappel", description="créer un rappel")
    @app_commands.describe(message="message à te rappeler")
    @app_commands.describe(date="format: dd/mm/yyyy hh:mm")
    async def pingSlash(self, interaction: discord.Interaction, message: str, date: str = None):

        if date is None:
            date = datetime.now(config.my_timezone)
            date = date.replace(hour=17, minute=0, second=0)
        else:
            try:
                date = datetime.strptime(date, "%d/%m/%Y %H:%M")
                date = date.replace(tzinfo=config.my_timezone)
            except ValueError:
                await interaction.response.send_message("Format de date invalide\nformat: dd/mm/yyyy hh:mm", ephemeral=True)
                return

        if date < datetime.now(config.my_timezone):
            await interaction.response.send_message("La date est déjà passée", ephemeral=True)
            return

        reminder = ReminderModel(
            user_id=interaction.user.id,
            message=message,
            timestamp=int(date.timestamp())
        )
        self.reminder.add_reminder(reminder)
        await interaction.response.send_message(f"Rappel noté pour le **{date.strftime('%d/%m/%Y à %H:%M')}**", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Reminder(bot))
