import os
from dotenv import load_dotenv

load_dotenv()

config_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.dirname(config_path)

token = os.environ.get("token")
reddit_id = os.environ.get("reddit_id")
reddit_secret = os.environ.get("reddit_secret")

prefix = [
    "!",
    "<@914226393565499412> ",
    "<@914226393565499412>",
    "<@!914226393565499412> ",
    "<@!914226393565499412>"
]
version = "5.1.0"
owner_id = 236853417681616906
main_server_id = 624629955099230228
timezone = "Europe/Paris"
