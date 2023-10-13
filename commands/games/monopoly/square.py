from typing import Optional
from commands.games.monopoly.data.squareData import SquareType

from commands.games.monopoly.player import Player



class Square:
    position: int
    type: SquareType
    name: str

    def __init__(self, position: int, type: SquareType, name: str) -> None:
        self.position = position
        self.type = type
        self.name = name


class Property(Square):
    owner: Optional[Player]
    price: int
    rent: int
    color: str
    multiplier: int

    def __init__(self, position: int, name: str, price: int, rent: int, color: str) -> None:
        super().__init__(position, SquareType.PROPERTY, name)
        self.owner = None
        self.price = price
        self.rent = rent
        self.color = color
        self.multiplier = 1
