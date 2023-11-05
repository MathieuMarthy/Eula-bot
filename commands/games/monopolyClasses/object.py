

import random


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


    def use(self, board, player):
        player.customDice = True
        return "Vous choisirez le résultat de votre prochain lancer de dé."


class DoubleDice(Object):
    id: int = 2
    price: int = 200
    name: str = "Dé double"


    def use(self, board, player):
        player.doubleDice = True
        return "Le résultat de votre prochain lancer de dé sera doublé."


class SwapPlayer(Object):
    id: int = 3
    price: int = 300
    name: str = "Echangeur de place avec un joueur aléatoire"


    def use(self, board, player):
    
        randomPlayer = random.choice(board.players)
        while randomPlayer == player:
            randomPlayer = random.choice(board.players)

        playerPosition = player.position

        board.playerChangePosition(player, randomPlayer.position)
        board.playerChangePosition(randomPlayer, playerPosition)

        return f"Vous avez échangé votre place avec **{randomPlayer.discord.display_name}.**"


class Immunity(Object):
    id: int = 4
    price: int = 500
    name: str = "Immunité de 2 tours"


    def use(self, board, player):
        player.immunity = 2
        return "Vous êtes immunisé pendant 2 tours."
