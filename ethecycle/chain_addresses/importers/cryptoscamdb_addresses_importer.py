"""
Scam addresses reported by cryptoscamdb.org. Curl data with:
curl --location --request GET 'https://api.cryptoscamdb.org/v1/addresses' > ethecycle/chain_addresses/raw_data/cryptoscamdb.addresses.json
"""
import json
from typing import List

from rich.panel import Panel
from rich.pretty import pprint

from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.config import Config
from ethecycle.models.blockchain import guess_chain_info_from_address
from ethecycle.models.wallet import Wallet
from ethecycle.util.filesystem_helper import RAW_DATA_DIR, get_lines
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *

SOURCE_URL = 'https://api.cryptoscamdb.org/v1/addresses'
CURL_OUTPUT_FILE = str(RAW_DATA_DIR.joinpath('cryptoscamdb.addresses.json.gz'))


def import_cryptoscamdb_addresses():
    """Import data from cryptoscamdb."""
    print_address_import(SOURCE_URL)
    wallets: List[Wallet] = []

    for address, data in json.loads("\n".join(get_lines(CURL_OUTPUT_FILE)))['result'].items():
        name = f"{data[0]['name']}: {data[0]['category']} ({data[0]['subcategory']})"
        chain_info = guess_chain_info_from_address(address)

        if chain_info is None:
            log.warning(f"No chain found for '{address}', skipping...")
            continue

        if Config.debug and len(data) > 1:
            console.print(Panel(f"{address} ({chain_info.__name__}) has {len(data)} entries", expand=False))
            console.print(f"Label: {name}")

            for hsh in data:
                pprint(hsh)
                print("----------------------------")

        wallets.append(
            Wallet(
                address=address,
                chain_info=chain_info,
                name=name,
                category=HACKERS,
                data_source=SOURCE_URL
            )
        )

    insert_addresses(wallets)
