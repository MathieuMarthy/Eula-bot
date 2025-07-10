import copy
from typing import Optional

from discord import Member
from commands.games.monopolyClasses.chanceEffect import ChanceEffect
from commands.games.monopolyClasses.object import CustomDice, Immunity, Object, SwapPlayer
from commands.games.monopolyClasses.square import Property, Square
from commands.games.monopolyClasses.data.const import CONST
from commands.games.monopolyClasses.data.squareData import PropertiesEmojis, SquareType




class Player:
    discord: Member
    emoji: str
    money: int
    position: int
    properties: list[Property]
    jail: bool
    jailTurn: int
    jailCard: bool
    objects: list[Object]

    # chance
    Switzerland_account: bool
    chance_effects: list[ChanceEffect]
    dice_multipler: int

    # object
    useObjectThisTurn: bool
    customDice: bool
    doubleDice: bool
    immunity: int


    def __init__(self, discord: Member, emoji: str) -> None:
        self.discord = discord
        self.emoji = emoji
        self.money = CONST.START_MONEY
        self.position = 0
        self.properties = []
        self.jail = False
        self.jailTurn = 0
        self.jailCard = False
        self.objects = []

        self.Switzerland_account = False
        self.chance_effects = []
        self.dice_multipler = None

        self.useObjectThisTurn = False
        self.customDice = False
        self.doubleDice = False
        self.immunity = 0
    

    def newTurn(self):
        self.useObjectThisTurn = False

        if self.immunity > 0:
            self.immunity -= 1


    def addMoney(self, amount: int):
        self.money = round(self.money + amount, 2)


    def loseMoney(self, amount: int):
        self.money = round(self.money - amount, 2)


    def multiplyMoney(self, pourcentage: int) -> int:
        """Multiply the money of the player

        Args:
            multiplier (int): the multiplier

        Returns:
            int: the money earned or lost
        """
        old = self.money
        self.money += round(self.money * pourcentage / 100, 2)
        return round(self.money - old, 2)


    def addChanceEffect(self, effect: ChanceEffect):
        self.chance_effects.append(effect)

    
    def addProperty(self, property: Property):
        self.properties.append(property)
    

    def removeProperty(self, property: Property):
        try:
            property.sell()
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
        self.position = newPosition

        if self.position >= 40:
            self.position -= 40
            self.addMoney(CONST.SALARY)


    def addPosition(self, amount: int):
        self.changePosition(self.position + amount)

    
    def die(self):
        for property in self.properties:
            property.sell()


    def buyObject(self, object: Object):
        self.addObject(object)
        self.loseMoney(object.price)


    def addObject(self, object: Object):
        newObject = copy.deepcopy(object)
        self.objects.append(newObject)


    def removeObject(self, object: Object):
        self.objects.remove(object)

    
    def useObject(self, board, object: Object) -> str:
        action = object.use(board, self)
        self.removeObject(object)
        return action


    def getObjectById(self, id: int) -> Optional[Object]:
        for obj in self.objects:
            if obj.id == id:
                return obj
        return None


    def buyProperty(self, property: Property):
        self.addProperty(property)
        self.loseMoney(property.price)

    def _getProperties(self) -> list[Property]:
        return [property for property in self.properties if isinstance(property, Property)]

    
    def getNumberOfProperties(self) -> int:
        return len(self._getProperties())
    
    
    def getNumberOfPropertiesAndRailroads(self) -> int:
        return len(self.properties)
    

    def getNumberOfObjects(self) -> int:
        return len(self.objects)


    def getRentOfaProperty(self, square: Square) -> int:
        """Get the rent of a property
        calculate with the multiplier and the number of properties in the color

        Args:
            position (Square): the square
        Returns:
            int: the rent
        """

        if square.type == SquareType.PROPERTY:
            property: Property = square

            if self.hasAllPropertiesInColor(property.color):
                return property.rent * CONST.MULTIPLIER_COLOR_GROUP * property.multiplier

            return round(property.rent * property.multiplier, 2)

        elif square.type == SquareType.RAILROAD:
            return CONST.RENT_RAILROAD * len([property for property in self.properties if property.type == SquareType.RAILROAD])
        
        return 0


    def hasAllPropertiesInColor(self, color: str) -> bool:
        """Check if the player has all the properties in a color

        Args:
            color (str): the color

        Returns:
            bool: if the player has all the properties in a color
        """
        return len(self.getPropertiesByColor(color)) == PropertiesEmojis.get_number_properties_in_color(color)


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


    def getPropertiesByColor(self, color: int) -> list[Property]:
        return [property for property in self._getProperties() if property.color == color]


    def sellProperties(self, properties: list[Property]) -> int:
        """Sell properties

        Args:
            properties (list[Property]): the properties to sell

        Returns:
            int: the money earned
        """

        totalPrice = 0
        for property in properties:
            price = property.sell()
            totalPrice += price
            
            self.removeProperty(property)
            self.addMoney(price)

        return totalPrice


    def getPriceForUpgrade(self) -> int:
        """Get the price for upgrade all the properties

        Returns:
            int: the price
        """
        return round(sum([property.price * CONST.UPGRADE_PORCENTAGE for property in self._getProperties()]))


    def upgradeProperties(self) -> int:
        """Upgrade all the properties"""

        for property in self._getProperties():
            if isinstance(property, Property):
                property.upgrade()

        self.loseMoney(self.getPriceForUpgrade())
