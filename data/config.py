import os

path = os.path.dirname(os.path.abspath(__file__))

with (open(f"{path}/token.txt", "r")) as f:
    token = f.read()

prefix = [
    "!",
    "<@914226393565499412> ",
    "<@914226393565499412>",
    "<@!914226393565499412> ",
    "<@!914226393565499412>"
]
version = "5.0.7"
owner_id = 236853417681616906
timezone = "Europe/Paris"
