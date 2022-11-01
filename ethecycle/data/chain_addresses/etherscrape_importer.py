"""
Load addresses from etherscrape gist.
"""
from os import path
from typing import Dict, List

from ethecycle.blockchains import get_chain_info
from ethecycle.data.chain_addresses.db import WALLETS_TABLE_NAME
from ethecycle.data.chain_addresses.address_db import delete_rows_for_data_source, insert_wallets
from ethecycle.util.filesystem_helper import RAW_DATA_DIR, files_in_dir, get_lines
from ethecycle.util.logging import log
from ethecycle.util.string_constants import ADDRESS_PREFIX
from ethecycle.wallet import Wallet

DATA_SOURCE = 'https://dune.com/crypto_oracle/wallets'
WALLETS_FROM_DUNE_SUFFIX = '_wallets_from_dune.txt.gz'


def import_wallets_from_dune() -> None:
    """Load all files matching the pattern raw_data/*wallets_from_dune.txt.gz."""
    wallets: List[Wallet] = []

    for file in [f for f in files_in_dir(RAW_DATA_DIR) if f.endswith(WALLETS_FROM_DUNE_SUFFIX)]:
        wallets.extend(extract_wallets_from_file(file))

    delete_rows_for_data_source(WALLETS_TABLE_NAME, DATA_SOURCE)
    insert_wallets(wallets)
