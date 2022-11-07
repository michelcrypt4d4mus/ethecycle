"""
Load addresses from etherscrape gist.
"""
from typing import Dict

from inflection import titleize

from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.chain_addresses.db.table_definitions import WALLETS_TABLE_NAME
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.util.filesystem_helper import RAW_DATA_DIR, get_lines
from ethecycle.util.logging import log, print_address_import
from ethecycle.models.wallet import Wallet

DATA_SOURCE = 'https://gist.githubusercontent.com/kheachang/4ce5a98140ad21129acd49aff0df11a8/raw/a049681e7168f7ea920e695f8b180b1fd9d921b0/gistfile1.txt'
SCRAPE_DATA_FILE = str(RAW_DATA_DIR.joinpath('etherscrape.txt.gz'))
ETHERSCAN_DONATE_ADDRESS = '0x71c7656ec7ab88b098defb751b7401b5f6d8976f'
ETHERSCAN_DONATE_LABEL = 'Etherscan: Donate'


def import_etherscrape_chain_addresses() -> None:
    """Load 3rd party data (apparently pulled from etherscan)."""
    print_address_import('etherscrape')
    wallet_addresses: Dict[str, Wallet] = {}

    for line in get_lines(SCRAPE_DATA_FILE):
        line_label, addresses = line.split(':')
        log.debug(f"Getting addresses for {line_label}...")

        if len(addresses) == 0:
            log.debug(f"    {line_label} has no addresses in etherscrape file...")
            continue

        for address in addresses.split(','):
            if not Ethereum.is_valid_address(address):
                raise ValueError(f"{address} is not a valid address! (line: {line}")

            address = address.lower()
            name = titleize(line_label) if address != ETHERSCAN_DONATE_ADDRESS else ETHERSCAN_DONATE_LABEL

            if address in wallet_addresses:
                if wallet_addresses[address].name != name:
                    wallet_addresses[address].name += f", {name}"
                    log.debug(f"  Added label '{name}' to {address}. New label: {wallet_addresses[address].name}")
            else:
                log.debug(f"  Processing address {address}...")
                wallet_addresses[address] = Wallet(address=address, chain_info=Ethereum, name=name, data_source=DATA_SOURCE)

    insert_addresses(list(wallet_addresses.values()))
