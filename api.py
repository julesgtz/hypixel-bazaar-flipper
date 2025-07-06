import json
import os
import requests
from rich.console import Console
import logging
from math import sqrt, log

from dotenv import load_dotenv

load_dotenv(f"{os.getcwd()}\.env")

user_console = Console()
logger = logging.getLogger(__name__)


class _API_DATA:
    API_KEY = os.getenv("API_KEY")
    BASE_URL = "https://api.hypixel.net"
    bazaar = BASE_URL + "/v2/skyblock/bazaar"


def fetcher(link: str, max_retry=3):
    retry = 0
    while retry < max_retry:
        logger.debug(f"Executing fetcher: {link=} {retry=} {max_retry=}")
        try:
            retry += 1
            response = requests.get(link, headers={"API-KEY": _API_DATA.API_KEY})
            logger.debug(f"Fetcher response for {link=}: {response}")
            assert response.ok, response.text
            return response.json()
        except Exception as e:
            logger.error(f"Error during request: {e}")
    return False


class API:
    def __init__(self, offline=False):
        self.bazaar = None
        self.offline = offline

    def reduce_dict_size(self):
        real_result = list()
        # alpha = 0.5
        for name, data in self.bazaar.items():
            if not data["sell_summary"] or not data["buy_summary"]:
                continue
            sell_price = data["sell_summary"][0]["pricePerUnit"]
            buy_price = data["buy_summary"][0]["pricePerUnit"]
            nbr_instasell = data["quick_status"]["sellMovingWeek"]
            nbr_instabuy = data["quick_status"]["buyMovingWeek"]
            liquidity = sqrt(nbr_instasell * nbr_instabuy)
            marge = buy_price - sell_price
            marge_pct = marge / sell_price
            # score = marge_pct * (liquidity**alpha)
            score = marge_pct * log(1 + marge_pct) * sqrt(liquidity)
            real_result.append(
                {
                    "name": name,
                    "sell_price": sell_price,
                    "buy_price": buy_price,
                    "liquidity": liquidity,
                    "score": score,
                    "marge": marge,
                    "marge_pct": marge_pct,
                    "nbr_instabuy": nbr_instabuy,
                    "nbr_instasell": nbr_instasell,
                }
            )
        self.bazaar = real_result
        return real_result

    def get_bazaar(self):
        user_console.print("[bold blue]Fetching bazaar data...[/bold blue]")
        response = fetcher(_API_DATA.bazaar)
        self.bazaar = response["products"]
        self.reduce_dict_size()
        self.dump_bazaar()
        user_console.print(
            "[bold green]bazaar data has been fetched and saved.[/bold green]"
        )
        return self.bazaar

    def dump_bazaar(self):
        with open("data/bazaar.json", "w", encoding="utf-8") as f:
            json.dump(self.bazaar, f, ensure_ascii=False, indent=4)
        logger.debug("Bazaar data dumped to file")

    def load_bazaar(self):
        with open("data/bazaar.json", "r", encoding="utf-8") as f:
            self.bazaar = json.load(f)
        logger.debug("Bazaar data loaded from file")

    def setup(self):
        if self.offline:
            self.load_bazaar()
        if self.bazaar:
            return
        user_console.print("[bold blue]Setting up API...[/bold blue]")
        self.get_bazaar()
        user_console.print("[bold green]API setup completed.[/bold green]")
