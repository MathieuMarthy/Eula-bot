import json
import random
from typing import Tuple

from discord import Member
from commands.games.monopolyClasses.data.SquareEmoji import SquareEmoji
from commands.games.monopolyClasses.data.const import CONST

from commands.games.monopolyClasses.player import Player
from commands.games.monopolyClasses.square import *


class Board:
    squares: list[Square] = []
    players: list[Player] = []
    _currentPlayer: int
    board: list[str] = []


    def __init__(self, players: list[Member]) -> None:
        self._currentPlayer = 0
        self.board = [
            ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"], # 0
            ["⬛", "🚗", "🟥", "❔", "🟥", "🟥", "🚉", "🟨", "🟨", "❔", "🟨", "👮", "⬛"], # 1
            ["⬛", "🟧", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "🟩", "⬛"], # 2
            ["⬛", "🟧", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "🟩", "⬛"], # 3
            ["⬛", "❔", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "❔", "⬛"], # 4
            ["⬛", "🟧", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "🟩", "⬛"], # 5
            ["⬛", "🚉", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "🚉", "⬛"], # 6
            ["⬛", "🟪", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "❔", "⬛"], # 7
            ["⬛", "🟪", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬜", "⬛"], # 8
            ["⬛", "❔", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "💵", "⬛"], # 9
            ["⬛", "🟪", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬜", "⬛"], # 10
            ["⬛", "⛓️", "🟦", "🟦", "❔", "🟦", "🚉", "💵", "🟫", "❔", "🟫", "⬅️",  "⬛"], # 11
            ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"], # 12
            # 0     1     2      3     4     5      6     7     8     9     10    11    12
        ]

        # Load squares 
        squares_json = json.load(open("commands/games/monopolyClasses/data/squares.json", "r", encoding="utf-8"))
        for i, square in enumerate(squares_json):
            if square["type"] == SquareType.PROPERTY.value:
                self.squares.append(
                    Property(
                        i,
                        square["name"],
                        square["price"],
                        square["rent"],
                        square["color"]
                    )
                )
            elif square["type"] == SquareType.TAX.value:
                self.squares.append(
                    Tax(
                        i,
                        square["name"],
                        square["price"]
                    )
                )
            elif square["type"] == SquareType.RAILROAD.value:
                self.squares.append(
                    Railroad(
                        i,
                        square["name"],
                        square["price"]
                    )
                )
            else:
                self.squares.append(
                    Square(
                        i,
                        square["type"],
                        square["name"]
                    )
                )

        # init players
        emojis = CONST.PLAYERS_EMOJIS
        random.shuffle(emojis)
        self.players = [Player(player, emojis.pop()) for player in players]

        random.shuffle(self.players)


    def rollDice(self):
        dice = random.randint(1, 12)
        
        currentPlayer = self.getCurrentPlayer()
        old_postion = currentPlayer.position

        currentPlayer.addPosition(dice)
        self.movePlayerOnBoard(currentPlayer, old_postion)

        return dice


    def playerPayRent(self, player: Player, square: Property) -> Tuple[bool, int]:
        """Player pay the rent to the owner of the square

        Args:
            player (Player): player who pay
            square (Property): square where the player is
        Returns:
            bool: if the player has enough money to pay the rent
            int: the rent
        """
        owner = self.getOwner(square)
        rent = owner.getRentOfaProperty(square)

        if player.money < rent:
            return (False, rent)

        owner.addMoney(rent)
        player.loseMoney(rent)

        return (True, rent)


    def nextPlayer(self):
        self._currentPlayer += 1

        if self._currentPlayer >= len(self.players):
            self._currentPlayer = 0


    def getSquareUnderPlayer(self, player: Player) -> Square:
        return self.squares[player.position]


    def getCurrentPlayer(self) -> Player:
        return self.players[self._currentPlayer]


    def getOwner(self, Property: Square):
        for player in self.players:
            if Property in player.properties:
                return player
        
        return None


    def buyProperty(self, player: Player, square: Property):
        player.buyProperty(square)

        if isinstance(square, Property) and player.hasAllPropertiesInColor(square.color):
            for square in player.getPropertiesByColor(square.color):
                index = self.getIndexInBoardSquare(square)
                self.board[index[0]][index[1]] = SquareEmoji[square.color]



    def movePlayerOnBoard(self, player: Player, old_position: int):
        old_index = self.getIndexInBoard(old_position)
        self.board[old_index[0]][old_index[1]] = self.getEmojiOnSquare(old_position)

        new_index = self.getIndexInBoard(player.position)
        self.board[new_index[0]][new_index[1]] = self.getEmojiOnSquare(player.position)


    def getPlayersOnSquare(self, square: int) -> list[Player]:
        return [player for player in self.players if player.position == square]


    def getEmojiOnSquare(self, square: int) -> str:
        players = self.getPlayersOnSquare(square)

        if len(players) == 1:
            return players[0].emoji
        elif len(players) > 1:
            return CONST.NUMBERS_EMOJIS[len(players) - 2]
        else:
            return "⬛"


    def getBoardStr(self) -> str:
        return "\n".join(["".join(line) for line in self.board])


    def getIndexInBoard(self, position: int) -> int:
        index = [12, 11]

        if 1 <= position <= 9:
            index = [12, 11 - position]
        elif 10 <= position <= 19:
            index = [11 - position % 10 , 0]
        elif 20 <= position <= 29:
            index = [0, 1 + position % 10]
        elif 30 <= position <= 39:
            index = [1 + position % 10, 12]

        return index


    def getIndexInBoardSquare(self, square: Square) -> list[int, int]:
        index = self.getIndexInBoard(square.position)

        if 1 <= square.position <= 9:
            index[0] = index[0] - 1
        elif 10 <= square.position <= 19:
            index[1] = index[1] + 1
        elif 20 <= square.position <= 29:
            index[0] = index[0] - 1
        elif 30 <= square.position <= 39:
            index[1] = index[1] + 1
        
        return index


    def luck(self, player: Player):
        num = random.randint(1, 1)

        action: str
        if num == 1:
            action = "Tu es très beau donc tu gagnes un concours de beauté. Tu gagnes 250 $. Non Tony cette carte ne fonctionne pas avec toi"
            
            if player.discord.id != 481528251605581854: # ID de Tony
                player.addMoney(250)

        return action
