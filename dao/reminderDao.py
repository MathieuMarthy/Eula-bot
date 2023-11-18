import os
import json

from data.config import path
from models.reminderModel import ReminderModel

class ReminderDao:
    __instance = None
    path = os.path.join(path, "databases", "reminder.json")
    reminder: dict

    @staticmethod
    def get_instance():
        if ReminderDao.__instance is None :
            ReminderDao.__instance = ReminderDao()
        return ReminderDao.__instance

    def __init__(self) -> None:
        self.load()

    def load(self):
        try:
            self.reminder = json.load(open(self.path, "r", encoding="utf-8"))
        except FileNotFoundError:
            self.reminder = {}
            self.save()

    def save(self):
        json.dump(self.reminder, open(self.path, "w", encoding="utf-8"), indent=4)

    def add_reminder(self, reminder: ReminderModel):
        if str(reminder.user_id) not in self.reminder:
            self.reminder[str(reminder.user_id)] = []
        self.reminder[str(reminder.user_id)].append(reminder.__dict__)
        self.save()

    def pop_reminder_to_send_at(self, timestamp: int):
        reminder_to_send = []
        
        for user_id in self.reminder.copy():
            for reminder in self.reminder[user_id]:
                if reminder["timestamp"] <= timestamp:
                    reminder_to_send.append(ReminderModel.from_dict(reminder))
                    self.reminder[user_id].remove(reminder)
        
        self.save()
        return reminder_to_send
