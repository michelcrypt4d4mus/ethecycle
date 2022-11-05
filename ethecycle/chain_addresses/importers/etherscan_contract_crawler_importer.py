"""
Import data from https://github.com/cl2089/etherscan-contract-crawler
"""
import json
from os import path
from pathlib import Path
from typing import List, Type

from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.blockchains.binance_smart_chain import BinanceSmartChain
from ethecycle.blockchains.blockchains import CHAIN_IDS, get_chain_info
from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.models.token import Token
from ethecycle.chain_addresses.address_db import (insert_tokens_from_data_source,
     insert_wallets_from_data_source)
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.util.filesystem_helper import files_in_dir, subdirs_of_dir
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *
from ethecycle.models.wallet import Wallet

SOURCE_REPO = GithubDataSource('cl2089/etherscan-contract-crawler')

CONTRACT_JSON_KEYS = set(['project', NAME, 'source', 'features'])

# Keys are folder names, values are blockchain names.
DIRS_TO_IMPORT = {
    'arb': ARBITRUM,
    'avax': AVALANCHE,
    'bsc': BINANCE_SMART_CHAIN,
    'eth': ETHEREUM,
}


def import_ethereum_contract_crawler_addresses():
    print_address_import(SOURCE_REPO.repo_url)
    wallets: List[Wallet] = []

    with SOURCE_REPO.local_repo_path() as root_dir:
        wallets.extend(_import_contracts(path.join(root_dir, 'contracts'), Ethereum))
        wallets.extend(_import_contracts(path.join(root_dir, 'bsc_contracts'), BinanceSmartChain))

    insert_wallets_from_data_source(wallets)


def _import_contracts(contracts_dir: str, chain_info: Type[ChainInfo]) -> List[Wallet]:
    console.print(f"Importing {chain_info._chain_str()}...", style='dim')
    wallets: List[Wallet] = []

    for file in [f for f in files_in_dir(contracts_dir, JSON)]: # if f.startswith('contracts_')]
        log.debug(f"Processing file: '{file}'")

        with open(file, 'r') as json_file:
            contracts = json.load(json_file)

        for contract in contracts:
            try:
                wallets.append(
                    Wallet(
                        label=contract['Contract Name'],
                        address=contract['Address'],
                        chain_info=chain_info,
                        category=CONTRACT,
                        data_source=SOURCE_REPO.repo_url
                    )
                )

                log.debug(f"Appended {wallets[-1]}...")
            except KeyError as e:
                log.warning(f"{e} parsing '{contract}'")

    return wallets
