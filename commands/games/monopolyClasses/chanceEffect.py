

class ChanceEffect:

    def __init__(self, turn: int) -> None:
        self.turn = turn


    def function(self, player) -> str:
        """This function is called each turn of the player who has the chance effect.

        Args:
            player (Player): The player who has the chance effect.

        Returns:
            str: The message to send to the channel.
        """
        pass
