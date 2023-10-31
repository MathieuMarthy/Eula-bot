

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


# TODO: faire plus d'objets et faire les fonctions use()
