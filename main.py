import os

import logging
import sys
from datetime import datetime
from console import ForgeApp
import argparse
from api import API

parser = argparse.ArgumentParser(description="hypixel-forge-profit parser")
parser.add_argument(
    "-o",
    "--offline",
    action="store_true",
    help="Use bazaar.json instead of connecting to the Hypixel API and scraping wiki",
)
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()


def now() -> str:
    return datetime.now().strftime("%d-%m-%Y")


os.mkdir("logs") if not os.path.exists("logs") else None
os.mkdir("data") if not os.path.exists("data") else None
logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    # level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"logs/{now()}.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    _api = API(args.offline)
    _api.setup()
    app = ForgeApp(_api.bazaar)
    app.run()
