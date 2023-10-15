import json
import random

import discord
from discord import Member
from commands.games.monopolyClasses.data.const import CONST

from commands.games.monopolyClasses.player import Player
from commands.games.monopolyClasses.square import *


class Board:
    squares: list[Square] = []
    lap: int = 1
    maxLap: int
    players: list[Player] = []
    _currentPlayer: int
    board: list[str] = []


    def __init__(self, maxLap: int, players: list[Member]) -> None:
        self.maxLap = maxLap
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
    

    def playerPayRent(self, player: Player, square: Property) -> bool:
        """Player pay the rent to the owner of the square

        Args:
            player (Player): player who pay
            square (Property): square where the player is
        Returns:
            bool: if the player has enough money to pay the rent
        """
        owner = self.getOwner(square)
        rent = owner.getRentOfaProperty(square.position)

        if player.money < rent:
            return False

        owner.addMoney(rent)
        player.loseMoney(rent)

        return True


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


    def movePlayerOnBoard(self, player: Player, old_position: int):
        old_index = self.getIndexInBoardWithPosition(old_position)
        self.board[old_index[0]][old_index[1]] = self.getEmojiOnSquare(old_position)

        new_index = self.getIndexInBoardWithPosition(player.position)
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
        

    def getLap(self) -> int:
        return max([player.lap for player in self.players])


    def getBoardStr(self) -> str:
        return "\n".join(["".join(line) for line in self.board])


    def getIndexInBoardWithPosition(self, position: int) -> int:
        index = (12, 11)

        if 1 <= position <= 10:
            index = (12, 11 - position)
        elif 11 <= position <= 19:
            index = (11 - position % 10 , 0)
        elif 20 <= position <= 30:
            index = (0, 1 + position % 10)
        elif 31 <= position <= 39:
            index = (1 + position % 10, 12)

        return index

    
    def luck(self, player: Player):
        pass
