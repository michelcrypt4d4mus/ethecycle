"""
Load files built from scrapes of Dune's wallet tag spellbook. Blockchain is embedded in
the filename (raw_data/ethereum_wallets_from_dune.txt.gz is for ethereum). The dumb 3 line
format in these files is a side effect of copy/pasting from the Dune web GUI.
"""
from os import path
from typing import Dict, List

from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.models.wallet import Wallet
from ethecycle.util.filesystem_helper import RAW_DATA_DIR, files_in_dir, get_lines
from ethecycle.util.logging import log, print_address_import

DATA_SOURCE = 'https://dune.com/crypto_oracle/wallets'
WALLETS_FROM_DUNE_SUFFIX = '_wallets_from_dune.txt.gz'


def import_wallets_from_dune() -> None:
    """Load all files matching the pattern raw_data/*wallets_from_dune.txt.gz."""
    print_address_import(DATA_SOURCE)
    wallets: List[Wallet] = []

    for file in [f for f in files_in_dir(RAW_DATA_DIR) if f.endswith(WALLETS_FROM_DUNE_SUFFIX)]:
        wallets.extend(extract_wallets_from_file(file))

    insert_addresses(wallets)


def extract_wallets_from_file(file) -> List[Wallet]:
    blockchain = path.basename(file).removesuffix(WALLETS_FROM_DUNE_SUFFIX)
    wallet_addresses: Dict[str, Wallet] = {}
    lines = get_lines(file)

    for i in range(0, len(lines) - 1, 3):
        address = lines[i]

        if not Ethereum.is_valid_address(address):
            raise ValueError(f"{address} does not start with {Ethereum.ADDRESS_PREFIXES[0]}!")
        elif address in wallet_addresses:
            log.warning(f"{address} already labeled '{wallet_addresses[address]}', discarding {lines[i + 1]}...")
        else:
            wallet_addresses[address] = Wallet(
                address=address,
                blockchain=blockchain,
                name=lines[i + 1],
                category=lines[i + 2].lower(),
                data_source=DATA_SOURCE
            )

    return list(wallet_addresses.values())
