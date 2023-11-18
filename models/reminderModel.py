from dataclasses import dataclass


@dataclass
class ReminderModel:
    user_id: int
    timestamp: int
    message: str

    def from_dict(dict: dict):
        return ReminderModel(
            user_id=dict["user_id"],
            timestamp=dict["timestamp"],
            message=dict["message"]
        )
