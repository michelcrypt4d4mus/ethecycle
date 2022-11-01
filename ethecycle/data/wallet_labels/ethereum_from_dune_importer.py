"""
Load files built from scrapes of Dune's wallet tag spellbook. Blockchain is embedded in
the filename (raw_data/ethereum_wallets_from_dune.txt.gz is for ethereum). The dumb 3 line
format in these files is a side effect of copy/pasting from the Dune web GUI.
"""
import gzip
import json
from os import listdir, path
from typing import Dict, List, Optional

from ethecycle.blockchains import get_chain_info
from ethecycle.blockchains.token import Token
from ethecycle.wallet import Wallet
from ethecycle.util.filesystem_helper import RAW_DATA_DIR, files_in_dir
from ethecycle.util.logging import log
from ethecycle.util.string_constants import ADDRESS_PREFIX
from ethecycle.util.time_helper import EXTRACTED_AT, current_timestamp_iso8601_str

DATA_SOURCE = 'https://dune.com/crypto_oracle/wallets'
WALLETS_FROM_DUNE_SUFFIX = '_from_dune.txt.gz'


def import_wallets_from_dune() -> None:
    """Load all files matching the pattern raw_data/*wallets_from_dune.txt.gz."""
    for file in [f for f in files_in_dir(RAW_DATA_DIR) if f.endswith(WALLETS_FROM_DUNE_SUFFIX)]:
        blockchain = path.basename(file).removesuffix(WALLETS_FROM_DUNE_SUFFIX)
        extracted_at = current_timestamp_iso8601_str()
        wallet_addresses: Dict[str, Wallet] = {}

        # Strip comment lines as we read from the gzip file.
        with gzip.open(file, 'rb') as file:
            lines = [line.decode().rstrip() for line in file if not line.startswith(b'#')]

        for i in range(0, len(lines) - 1, 3):
            address = lines[i]

            if not address.startswith(ADDRESS_PREFIX):
                raise ValueError(f"{address} does not start with {ADDRESS_PREFIX}!")
            elif address in wallet_addresses:
                log.warning(f"{address} already labeled '{wallet_addresses[address]}', discarding {lines[i + 1]}...")
            else:
                wallet_addresses[address] = Wallet(
                    address,
                    get_chain_info(blockchain),
                    lines[i + 1],
                    lines[i + 2].lower()
                )

