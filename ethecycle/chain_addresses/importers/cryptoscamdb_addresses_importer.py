"""
Scam addresses reported by cryptoscamdb.org. Curl data with:
curl --location --request GET 'https://api.cryptoscamdb.org/v1/addresses' > ethecycle/chain_addresses/raw_data/cryptoscamdb.addresses.json
"""
import json
from typing import List

from rich.panel import Panel
from rich.pretty import pprint

from ethecycle.blockchains.blockchains import guess_chain_info_from_address
from ethecycle.chain_addresses.address_db import insert_wallets_from_data_source
from ethecycle.chain_addresses.db.table_definitions import WALLETS_TABLE_NAME
from ethecycle.config import Config
from ethecycle.util.filesystem_helper import RAW_DATA_DIR, get_lines
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *
from ethecycle.wallet import Wallet

SOURCE_URL = 'https://api.cryptoscamdb.org/v1/addresses'
CURL_OUTPUT_FILE = str(RAW_DATA_DIR.joinpath('cryptoscamdb.addresses.json.gz'))


def import_cryptoscamdb_addresses():
    """Import data from ethereum-lists tokens repo."""
    print_address_import(SOURCE_URL)
    wallets: List[Wallet] = []
    #file_contents = "\n".join(get_lines(CURL_OUTPUT_FILE))

    for address, data in json.loads("\n".join(get_lines(CURL_OUTPUT_FILE)))['result'].items():
        label = f"{data[0]['name']}: {data[0]['category']} ({data[0]['subcategory']})"
        chain_info = guess_chain_info_from_address(address)

        if chain_info is None:
            log.warning(f"No chain found for '{address}', skipping...")
            continue

        if Config.debug and len(data) > 1:
            console.print(Panel(f"{address} ({chain_info.__name__}) has {len(data)} entries", expand=False))
            console.print(f"Label: {label}")

            for hsh in data:
                pprint(hsh)
                print("----------------------------")

        wallets.append(
            Wallet(
                address=address,
                chain_info=chain_info,
                label=label,
                category=HACKERS,
                data_source=SOURCE_URL
            )
        )

    insert_wallets_from_data_source(wallets)
