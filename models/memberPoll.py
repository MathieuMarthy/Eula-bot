

class MemberPoll:

    def __init__(self, memberId: int, vote: str) -> None:
        self.memberId = memberId
        self.vote = vote


    def __lt__(self, other):
        return self.vote > other.vote
