import pytz
import os
from dotenv import load_dotenv

load_dotenv()

config_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.dirname(config_path)
my_timezone = pytz.timezone("Europe/Paris")

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
version = "5.2.0"
owner_id = 236853417681616906
main_server_id = 624629955099230228
timezone = "Europe/Paris"

riot_api_url = "https://europe.api.riotgames.com"
riot_api_url_euw = "https://euw1.api.riotgames.com"
riot_api_ddragon = "https://ddragon.leagueoflegends.com/cdn/14.1.1"
riot_api_key = os.environ.get("riot_api_key")
