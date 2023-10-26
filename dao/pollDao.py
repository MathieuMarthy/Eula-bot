import json
import os

from models.memberPoll import MemberPoll

project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class pollDao:
    __instance = None

    @staticmethod
    def get_instance():
        if pollDao.__instance is None :
            pollDao.__instance = pollDao()
        return pollDao.__instance

    def __init__(self) -> None:
        self.poll_file = json.load(open(os.path.join(project_path, "data", "poll.json"), "r", encoding="utf-8"))


    def save_poll_file(self):
        json.dump(self.poll_file, open(os.path.join(project_path, "data", "poll.json"), "w", encoding="utf-8"), indent=4)


    def create_poll(self, guild: int, channel: int, poll_msg_id: int, end_timestamp: int, question: str, choix: list):
        if str(guild) not in self.poll_file:
            self.poll_file[str(guild)] = {}

        if str(channel) not in self.poll_file[str(guild)]:
            self.poll_file[str(guild)][str(channel)] = {}
        
        self.poll_file[str(guild)][str(channel)][str(poll_msg_id)] = {
            "question": question,
            "end_date": end_timestamp,
            "choix": choix,
            "vote": {}
        }
        self.save_poll_file()


    def add_member_poll(self, guild: int, channel: int, poll_msg_id: int, member_id: int, choix: int):
        self.poll_file[str(guild)][str(channel)][str(poll_msg_id)]["vote"][str(member_id)] = choix
        self.save_poll_file()


    def get_vote_poll(self, guild: int, channel: int, poll_msg_id: int):
        return self.poll_file[str(guild)][str(channel)][str(poll_msg_id)]["vote"]


    def get_poll(self, guild: int, channel: int, poll_msg_id: int):
        return self.poll_file[str(guild)][str(channel)][str(poll_msg_id)]


    def get_members_poll(self, guild: int, channel: int, poll_msg_id: int):
        questions = self.poll_file[str(guild)][str(channel)][str(poll_msg_id)]["choix"]

        members = [
            MemberPoll(memberId, questions[vote])
            for memberId, vote in self.poll_file[str(guild)][str(channel)][str(poll_msg_id)]["vote"].items()
        ]
        members.sort()
        return members


    def get_all_poll(self):
        return self.poll_file


    def remove_poll(self, guild: int, channel: int, poll_msg_id: int):
        del self.poll_file[str(guild)][str(channel)][str(poll_msg_id)]

        if self.poll_file[str(guild)][str(channel)] == {}:
            del self.poll_file[str(guild)][str(channel)]
        
        if self.poll_file[str(guild)] == {}:
            del self.poll_file[str(guild)]

        self.save_poll_file()
