from commands.games.monopolyClasses.data.const import CONST
from commands.games.monopolyClasses.data.squareData import SquareType


class Square:
    position: int
    type: SquareType
    name: str

    def __init__(self, position: int, type: SquareType, name: str) -> None:
        self.position = position
        self.type = type
        self.name = name


class Tax(Square):
    price: int

    def __init__(self, position: int, name: str, price: int) -> None:
        super().__init__(position, SquareType.TAX.value, name)
        self.price = price


class Railroad(Square):
    price: int

    def __init__(self, position: int, name: str, price: int) -> None:
        super().__init__(position, SquareType.RAILROAD.value, name)
        self.price = price


class Property(Square):
    price: int
    rent: int
    color: str
    multiplier: int

    def __init__(self, position: int, name: str, price: int, rent: int, color: str) -> None:
        super().__init__(position, SquareType.PROPERTY.value, name)
        self.price = price
        self.rent = rent
        self.color = color
        self.multiplier = 1

    
    def upgrade(self):
        self.multiplier += 0.2


    def getSellPrice(self) -> int:
        return round(self.price / CONST.MORTGAGE_DIVIDER)

    def sell(self) -> int:
        """Sell the property

        Returns:
            int: the money earned
        """
        self.multiplier = 1
        return self.getSellPrice()
