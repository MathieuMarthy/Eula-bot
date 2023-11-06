import json
import random
from typing import Tuple

from discord import Member
from commands.games.monopolyClasses.chanceEffect import ChanceEffect
from commands.games.monopolyClasses.data.const import CONST
from commands.games.monopolyClasses.data.squareData import PropertiesEmojis
from commands.games.monopolyClasses.object import *

from commands.games.monopolyClasses.player import Player
from commands.games.monopolyClasses.square import *


class Board:
    squares: list[Square] = []
    players: list[Player] = []
    objects: list[Object] = []
    _currentPlayer: int
    board: list[str] = []

    privateJokes: bool


    def __init__(self, players: list[Member], privatesJokes: bool) -> None:
        self._currentPlayer = 0
        self.board = [
            ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"], # 0
            ["⬛", "🛒", "🟥", "❔", "🟥", "🟥", "🚉", "🟨", "🟨", "❔", "🟨", "👮", "⬛"], # 1
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
            elif square["type"] == SquareType.TAX:
                self.squares.append(
                    Tax(
                        i,
                        square["name"],
                        square["price"]
                    )
                )
            elif square["type"] == SquareType.RAILROAD:
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

        # init objects
        self.objects = [
            CustomDice(),
            DoubleDice(),
            SwapPlayer(),
            Immunity()
        ]

        self.privateJokes = privatesJokes


    def rollDice(self, player: Player, dice: int = None) -> int:
        if dice is None:
            dice = random.randint(1, 12)

        # == chance effects & objects ==
        if player.dice_multipler is not None:
            dice = dice // player.dice_multipler
            player.dice_multipler = None
        
        if player.doubleDice:
            dice *= 2
            player.doubleDice = False

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

        enoughMoney = player.money < rent

        owner.addMoney(rent)
        player.loseMoney(rent)

        return (enoughMoney, rent)


    def updatePropertiesEmojisOnBoard(self):
        for square in self.squares:
            index = self.getIndexInBoardSquare(square)

            if isinstance(square, Property):
                owner = self.getOwner(square)
                if owner is not None and owner.hasAllPropertiesInColor(square.color):
                    self.board[index[0]][index[1]] = PropertiesEmojis.get_crown_emoji_by_color(square.color)
                else:
                    self.board[index[0]][index[1]] = PropertiesEmojis.get_emojis_by_color(square.color)


    def nextPlayer(self):
        self._currentPlayer += 1

        if self._currentPlayer >= len(self.players):
            self._currentPlayer = 0


    def playerDie(self, player: Player):
        self.players.remove(player)
        player.die()


    def getSquareUnderPlayer(self, player: Player) -> Square:
        return self.squares[player.position]


    def getCurrentPlayer(self) -> Player:
        return self.players[self._currentPlayer]


    def getOwner(self, Property: Square):
        for player in self.players:
            if Property in player.properties:
                return player
        
        return None


    def getObjectById(self, id: int) -> Object:
        for obj in self.objects:
            if obj.id == id:
                return obj
        return None


    def buyProperty(self, player: Player, square: Property):
        player.buyProperty(square)
        self.updatePropertiesEmojisOnBoard()


    def sellProperties(self, player: Player, squares: list[Square]):
        total = player.sellProperties(squares)
        self.updatePropertiesEmojisOnBoard()
        return total


    def movePlayerOnBoard(self, player: Player, old_position: int):
        old_index = self.getIndexInBoard(old_position)
        self.board[old_index[0]][old_index[1]] = self.getEmojiOnSquare(old_position)

        new_index = self.getIndexInBoard(player.position)
        self.board[new_index[0]][new_index[1]] = self.getEmojiOnSquare(player.position)


    def currentPlayerWin(self) -> bool:
        return len(self.players) == 1
    

    def playerGoToJail(self, player: Player):
        old_position = player.position
        player.goToJail()
        self.movePlayerOnBoard(player, old_position)


    def playerChangePosition(self, player: Player, position: int):
        old_position = player.position
        player.changePosition(position)
        self.movePlayerOnBoard(player, old_position)


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

        if 0 <= square.position <= 9:
            index[0] = index[0] - 1
        elif 10 <= square.position <= 19:
            index[1] = index[1] + 1
        elif 20 <= square.position <= 29:
            index[0] = index[0] + 1
        elif 30 <= square.position <= 39:
            index[1] = index[1] - 1
        
        return index


    def chance(self, current_player: Player):
        action: str


        if self.privateJokes:
            num = random.randint(0, 21)
        else:
            num = random.randint(1, 21)

        if num == 0:
            action = f"Tony a arrêté d'être gay, tu perds moins d'argent en capote, gagne **200 {CONST.MONEY_SYMBOL}**."
            current_player.addMoney(200)

        if num == 1:
            action = f"Tu es très beau donc tu gagnes un concours de beauté. Tu gagnes **250 {CONST.MONEY_SYMBOL}**."

            if self.privateJokes:
                action += "Non Tony cette carte ne fonctionne pas avec toi."
                if current_player.discord.id != 481528251605581854: # ID de Tony
                    current_player.addMoney(250)

        elif num == 2:
            action = "Vous gagnez une carte sortie de prison. Vous pouvez l'utiliser quand vous voulez."
            current_player.addJailCard()

        elif num == 3:
            action = f"Tu fais commerce de ton eau de bain de femboy, chaque joueur en achète 1 pot à **50 {CONST.MONEY_SYMBOL}**."

            for player in self.players:
                if player == current_player:
                    continue
                
                player.loseMoney(50)
                current_player.addMoney(50)

        elif num == 4:
            if current_player.Switzerland_account:
                return self.chance(current_player)

            action = "Tu ouvres un compte bancaire en suisse ! Tu es maintenant immunisé contre les taxes."
            current_player.Switzerland_account = True

        elif num == 5:
            action = f"Tu as gagné **100 {CONST.MONEY_SYMBOL}** à la loterie !"
            current_player.addMoney(100)

        elif num == 6:
            action = "Un investisseur chinois 😑 investit dans tes propriétés. Le prix de tes propriétés augmente de 10 %."

            for property in current_player.properties:
                property.upgrade(0.1)

        elif num == 7:
            action = f"Tu touches l'héritage de tonton jean-ma, gagne **200 {CONST.MONEY_SYMBOL}**."
            current_player.addMoney(200)

        elif num == 8:
            action = f"\"La terre, elle n'est pas verte, elle est bleue\" Jojo n'aime pas les écolos et te casse la gueule, tu dois payer les frais d'hopitaux  **-200 {CONST.MONEY_SYMBOL}.**"
            current_player.loseMoney(200)

        elif num == 9:
            action = f"Tu as commencé à jouer à League of Legends, tu achètes trop de skins ... **-300 {CONST.MONEY_SYMBOL}**."
            current_player.loseMoney(300)

        elif num == 10:
            action = f"Tu as laissé ta femme conduire ta voiture, elle a eu un accident, tu dois payer **300 {CONST.MONEY_SYMBOL}** de réparation."
            current_player.loseMoney(300)

        elif num == 11:
            action = f"La police a regardé ton historique, tu dois payer **200 {CONST.MONEY_SYMBOL}** d'amende et tu **vas en prison**."
            current_player.loseMoney(200)
            self.playerGoToJail(current_player)

        elif num == 12:
            action = f"Tu as grand mère est morte, tu hérites de **1 000 {CONST.MONEY_SYMBOL}**."
            current_player.addMoney(1_000)

        elif num == 13:
            action = f"Tu as voté Sandrine Rousseau..., tu perds **100 {CONST.MONEY_SYMBOL}**."
            current_player.loseMoney(100)

        elif num == 14:

            if current_player.getNumberOfProperties() > 1:
                
                for player in self.players:
                    if player.getNumberOfProperties() > 1:
                        
                        # penser au émojis quand on a toutes les propriétés d'une couleur
                        property1 = random.choice(current_player.properties)
                        property2 = random.choice(player.properties)
                        action = f"Tu échanges une propriété avec **{player.discord.display_name}**.\nTu as donné **{property1.name}** et tu as reçu **{property2.name}**."

                        current_player.removeProperty(property1)
                        player.removeProperty(property2)

                        current_player.addProperty(property2)
                        player.addProperty(property1)
                        return action

            return self.chance(current_player)

        elif num == 15:
            if len(current_player.properties) == 0:
                return self.chance(current_player)

            action = "Un huissier vient chez toi et constate que tout n'est pas en règle, tu perds une propriété au hasard."
            property = random.choice(current_player.properties)
            current_player.removeProperty(property)

        elif num == 16:
            action = "Blitzcrank vous gank avec un grab, tu es téléporté sur une case aléatoire."
            self.playerChangePosition(current_player, random.randint(0, 39))
        
        elif num == 17:
            action = f"SIUUUUUU ! Oh mon dieu Ronaldo sort d'un buisson et te donne **300 {CONST.MONEY_SYMBOL}**."
            current_player.addMoney(300)
        
        elif num == 18:
            action = f"Tu écris le meilleur hentai loli, gagne **300 {CONST.MONEY_SYMBOL}** mais perds ta santée mentale et **vas en prison**."
            current_player.addMoney(300)
            self.playerGoToJail(current_player)

        elif num == 19:
            action = "Tout le monde retourne à la case départ."

            for player in self.players:
                self.playerChangePosition(player, 0)

        elif num == 20:
            action = "Tu investis dans le bitcoin pendant 3 tours, ton salaire évolura en fonction du cours du bitcoin."

            chanceEffect = ChanceEffect(3)
            chanceEffect.function = lambda player: (
                evolution := random.randint(-10, 10),
                earn := player.multiplyMoney(evolution),
                word := "augmenté" if evolution > 0 else "diminué",
                f"Le cours du bitcoin à {word} de {abs(evolution)} %\nVotre salaire à {word} de **{abs(earn)} {CONST.MONEY_SYMBOL}**."
            )
            current_player.addChanceEffect(chanceEffect)

        elif num == 21:
            action = f"Tu gagnes le concours du plus gros mangeur, tu remportes **100 {CONST.MONEY_SYMBOL}** mais au prochain tour, tes dés sont dévisés par 2"

            current_player.dice_multipler = 0.5
            chanceEffect = ChanceEffect(1)
            chanceEffect.function = lambda player: (
                "Tes dés sont divisés par 2."
            )

        return action
