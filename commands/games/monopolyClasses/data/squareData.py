from enum import Enum


numberPropertiesInColor = {
    1: 2,
    2: 3,
    3: 3,
    4: 3,
    5: 3,
    6: 3,
    7: 3,
    8: 2,
}

class SquareType(Enum):
    PROPERTY = 1
    RAILROAD = 2
    LUCK = 3
    TAX = 4
    JAIL = 5
    START = 6
    GO_TO_JAIL = 7
