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
    board: list[str] = []


    def __init__(self, maxLap: int, players: list[Member]) -> None:
        self.maxLap = maxLap
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
        squares_json = json.load(open("commands/games/monopolyClasses/data/squares.json"))
        for i, square in enumerate(squares_json):
            if square["type"] == SquareType.PROPERTY:
                self.squares.append(
                    Property(
                        i,
                        square["name"],
                        square["price"],
                        square["rent"],
                        square["color"]
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


    def waitInteraction(self):
        pass


    def getBoardStr(self) -> str:
        newBoard = self.board

        players_positions = {}
        for player in self.players:
            key = self.getIndexInBoardWithPosition(player.position)

            if key not in players_positions:
                players_positions[key] = []
            
            players_positions[key].append(player)        


        for position, players in players_positions.items():
            
            if len(players) == 1:
                newBoard[position[0]][position[1]] = players[0].emoji
            else:
                newBoard[position[0]][position[1]] = CONST.NUMBERS_EMOJIS[len(players) - 2]

        return "\n".join(["".join(line) for line in newBoard])


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


    def movePlayer(self, player: Player, amount: int):
        player.addPosition(amount)

    
    def luck(self, player: Player):
        pass
