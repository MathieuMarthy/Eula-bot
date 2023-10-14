from typing import Optional

from discord import Member
from commands.games.monopolyClasses.square import Property
from commands.games.monopolyClasses.data.const import CONST
from commands.games.monopolyClasses.data.squareData import numberPropertiesInColor




class Player:
    discord: Member
    emoji: str
    money: int
    position: int
    properties: list[Property]
    jail: bool
    jailTurn: int
    jailCard: bool
    lap: int
    
    def __init__(self, discord: Member, emoji: str) -> None:
        self.discord = discord
        self.emoji = emoji
        self.money = 1500
        self.position = 0
        self.properties = []
        self.jail = False
        self.jailTurn = 0
        self.jailCard = False
        self.lap = 1


    def addMoney(self, amount: int):
        self.money -= amount

    
    def addLap(self):
        self.lap += 1


    def loseMoney(self, amount: int):
        self.money += amount

    
    def addProperty(self, property: Property):
        self.properties.append(property)
    

    def removeProperty(self, property: Property):
        try:
            self.properties.remove(property)
        except:
            pass
    

    def leaveJail(self):
        self.jail = False
        self.jailTurn = 0


    def goToJail(self):
        self.jail = True
        self.jailTurn = 0
        self.position = 10

    
    def useJailCard(self):
        self.jailCard = False
        self.jailTurn = 0
    

    def addJailCard(self):
        self.jailCard = True


    def changePosition(self, newPosition: int):
        self.position += newPosition

        if self.position >= 40:
            self.position -= 40


    def addPosition(self, amount: int):
        self.changePosition(self.position + amount)


    def buyProperty(self, property: Property):
        self.addProperty(property)
        self.loseMoney(property.price)


    def getRentOfaProperty(self, position: int) -> int:
        """Get the rent of a property
        calculate with the multiplier and the number of properties in the color

        Args:
            position (int): position of the property

        Returns:
            int: the rent
        """
        property = self.getPropertyByPosition(position)

        if self.getPropertiesByColor(property.color) == numberPropertiesInColor[property.color]:
            return property.rent * CONST.MULTIPLIER_COLOR_GROUP * property.multiplier

        return property.rent * property.multiplier


    def getPropertyByPosition(self, position: int) -> Optional[Property]:
        """Get a property by position

        Args:
            position (int): position of the property

        Returns:
            Optional[Property]: the property or None if not found
        """
        for property in self.properties:
            if property.position == position:
                return property
        return None


    def getPropertiesByColor(self, color: str) -> list[Property]:
        return [property for property in self.properties if property.color == color]


    def mortgageProperties(self, properties: list[Property]):
        for property in properties:
            self.addMoney(property.price / CONST.MORTGAGE_DIVIDER)
