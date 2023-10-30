

class Object:
    id: int
    name: str
    price: int 

    def use(self, board, player) -> str:
        pass


class CustomDice(Object):
    id: int = 1
    price: int = 400
    name: str = "Dé pipé"


class DoubleDice(Object):
    id: int = 2
    price: int = 200
    name: str = "Dé double"
