"""
Load addresses from etherscrape gist.
"""
from typing import Dict

from inflection import titleize

from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.data.chain_addresses.db import WALLETS_TABLE_NAME
from ethecycle.data.chain_addresses.address_db import delete_rows_from_source, insert_wallets
from ethecycle.util.filesystem_helper import RAW_DATA_DIR, get_lines
from ethecycle.util.logging import console, log
from ethecycle.util.string_constants import ADDRESS_PREFIX
from ethecycle.wallet import Wallet

DATA_SOURCE = 'https://gist.githubusercontent.com/kheachang/4ce5a98140ad21129acd49aff0df11a8/raw/a049681e7168f7ea920e695f8b180b1fd9d921b0/gistfile1.txt'
SCRAPE_DATA_FILE = str(RAW_DATA_DIR.joinpath('etherscrape.txt.gz'))
ETHERSCAN_DONATE_ADDRESS = '0x71c7656ec7ab88b098defb751b7401b5f6d8976f'
ETHERSCAN_DONATE_LABEL = 'Etherscan: Donate'


def import_etherscrape_chain_addresses() -> None:
    """Load 3rd party data (apparently pulled from etherscan)."""
    console.print("Importing etherscrape chain addresses...")
    wallet_addresses: Dict[str, Wallet] = {}

    for line in get_lines(SCRAPE_DATA_FILE):
        line_label, addresses = line.split(':')
        log.debug(f"Getting addresses for {line_label}...")

        if len(addresses) == 0:
            log.debug(f"    {line_label} has no addresses in etherscrape file...")
            continue

        for address in addresses.split(','):
            if not address.startswith(ADDRESS_PREFIX):
                raise ValueError(f"{address} is not a valid address! (line: {line}")

            address = address.lower()
            label = titleize(line_label) if address != ETHERSCAN_DONATE_ADDRESS else ETHERSCAN_DONATE_LABEL

            if address in wallet_addresses:
                if wallet_addresses[address].label != label:
                    wallet_addresses[address].label += f", {label}"
                    log.debug(f"  Added label '{label}' to {address}. New label: {wallet_addresses[address].label}")
            else:
                log.debug(f"  Processing address {address}...")
                wallet_addresses[address] = Wallet(address, Ethereum, label, data_source=DATA_SOURCE)

    delete_rows_from_source(WALLETS_TABLE_NAME, DATA_SOURCE)
    insert_wallets(list(wallet_addresses.values()))
