"""
Load files built from scrapes of Dune's wallet tag spellbook. Blockchain is embedded in
the filename (raw_data/ethereum_wallets_from_dune.txt.gz is for ethereum). The dumb 3 line
format in these files is a side effect of copy/pasting from the Dune web GUI.
"""
from os import path
from typing import Dict, List

from ethecycle.blockchains import get_chain_info
from ethecycle.data.chain_addresses.db import WALLETS_TABLE_NAME
from ethecycle.data.chain_addresses.address_db import delete_rows_from_source, insert_wallets
from ethecycle.util.filesystem_helper import RAW_DATA_DIR, files_in_dir, get_lines
from ethecycle.util.logging import console, log
from ethecycle.util.string_constants import ADDRESS_PREFIX
from ethecycle.wallet import Wallet

DATA_SOURCE = 'https://dune.com/crypto_oracle/wallets'
WALLETS_FROM_DUNE_SUFFIX = '_wallets_from_dune.txt.gz'


def import_wallets_from_dune() -> None:
    """Load all files matching the pattern raw_data/*wallets_from_dune.txt.gz."""
    console.print("Importing Dune Analytics chain addresses...")
    wallets: List[Wallet] = []

    for file in [f for f in files_in_dir(RAW_DATA_DIR) if f.endswith(WALLETS_FROM_DUNE_SUFFIX)]:
        wallets.extend(extract_wallets_from_file(file))

    delete_rows_from_source(WALLETS_TABLE_NAME, DATA_SOURCE)
    insert_wallets(wallets)


def extract_wallets_from_file(file) -> List[Wallet]:
    blockchain = path.basename(file).removesuffix(WALLETS_FROM_DUNE_SUFFIX)
    wallet_addresses: Dict[str, Wallet] = {}
    lines = get_lines(file)

    for i in range(0, len(lines) - 1, 3):
        address = lines[i]

        if not address.startswith(ADDRESS_PREFIX):
            raise ValueError(f"{address} does not start with {ADDRESS_PREFIX}!")
        elif address in wallet_addresses:
            log.warning(f"{address} already labeled '{wallet_addresses[address]}', discarding {lines[i + 1]}...")
        else:
            wallet_addresses[address] = Wallet(
                address=address,
                chain_info=get_chain_info(blockchain),
                label=lines[i + 1],
                category=lines[i + 2].lower(),
                data_source=DATA_SOURCE
            )

    return list(wallet_addresses.values())
