from typing import Optional, Tuple
import requests

from data.config import riot_api_key, riot_api_url, riot_api_ddragon, riot_api_url_euw
from errors.api import ApiError, ApiKeyError, ApiNotFoundError



class RiotApi:
    
    def __init__(self) -> None:
        self.headers = {
            "X-Riot-Token": riot_api_key
        }

    
    def __get_url(self, path: str, riot_api: str = riot_api_url) -> str:
        return f"{riot_api}/{path}"

    
    def __make_request(self, url: str) -> requests.Response:
        res = requests.get(url, headers=self.headers)

        if res.status_code in [401, 403]:
            raise ApiKeyError("Erreur de connexion à l'API Riot")
        
        elif res.status_code == 404:
            raise ApiNotFoundError("Impossible de trouver votre compte LoL")
        
        elif not res.ok:
            raise ApiError("Erreur de connexion à l'API Riot")
        
        return res

    
    def get_player_puuid_name(self, name: str, tag: str) -> Tuple[str, str]:
        name_clean = name.replace(" ", "%20")
        path = f"riot/account/v1/accounts/by-riot-id/{name_clean}/{tag}"

        url = self.__get_url(path)
        res = self.__make_request(url)
        json = res.json()

        return json["puuid"], json["gameName"]


    def get_player_id_ppId(self, puuid: str) -> tuple[str, str]:
        path = f"lol/summoner/v4/summoners/by-puuid/{puuid}"

        res = self.__make_request(self.__get_url(path, riot_api_url_euw))
        json = res.json()

        return  json["id"], json["profileIconId"]

    
    def get_rank_data(self, player_id: str) -> Optional[dict]:
        path = f"lol/league/v4/entries/by-summoner/{player_id}"

        res = self.__make_request(self.__get_url(path, riot_api_url_euw))

        if res.status_code != 200:
            return None

        return res.json()


    def get_profile_icon_url(self, icon_id: int) -> str:
        return f"{riot_api_ddragon}/img/profileicon/{icon_id}.png"
