from enum import Enum


class PropertiesEmojis:


    def get_emojis_by_color(color: int) -> str:
        """Get the emojis by color

        Args:
            color (str): the color

        Returns:
            list[str]: the emojis
        """
        return {
            1: "🟫",
            2: "🟦",
            3: "🟪",
            4: "🟧",
            5: "🟥",
            6: "🟨",
            7: "🟩",
            8: "⬜",
        }[color]


    def get_crown_emoji_by_color(color: int) -> str:
        """Get the crown emoji

        Returns:
            str: the crown emoji
        """
        return {
            1: "<:brs:1163875166946869400>",
            2: "<:bls:1163875169027248269>",
            3: "<:ps:1163875175243202680>",
            4: "<:os:1163875173880053870>",
            5: "<:rs:1163875178342785034>",
            6: "<:ys:1163875163809529897>",
            7: "<:gs:1163875171753541632>",
            8: "<:ws:1163875181123616891>"
        }[color]


    def get_number_properties_in_color(color: int) -> int:
        """Get the number of properties in a color

        Args:
            color (str): the color

        Returns:
            int: the number of properties
        """
        return {
            1: 2,
            2: 3,
            3: 3,
            4: 3,
            5: 3,
            6: 3,
            7: 3,
            8: 2,
        }[color]
    
    

class SquareType(Enum):
    PROPERTY = 1
    RAILROAD = 2
    LUCK = 3
    TAX = 4
    JAIL = 5
    START = 6
    GO_TO_JAIL = 7
