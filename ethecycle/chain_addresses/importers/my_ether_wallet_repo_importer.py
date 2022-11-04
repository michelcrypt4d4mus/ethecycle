"""
MyEtherWallet has repo called ethereum-lists that has a bunch of black and whitelist stuff.
"""
import json
from os import path
from typing import List

from ethecycle.models.token import Token
from ethecycle.chain_addresses.address_db import insert_tokens_from_data_source
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.util.logging import print_address_import, print_dim
from ethecycle.util.string_constants import *

MY_ETHER_WALLET_REPO = GithubDataSource('MyEtherWallet/ethereum-lists')

# Keys are folder names, values are blockchain names.
DIRS_TO_IMPORT = {
    'bsc': BINANCE_SMART_CHAIN,
    'eth': ETHEREUM,
    'matic': 'Polygon'
}


def import_my_ether_wallet_addresses():
    _import_tokens_addresses()


def _import_tokens_addresses():
    """Import data from ethereum-lists tokens repo."""
    print_address_import(MY_ETHER_WALLET_REPO.repo_url)

    with MY_ETHER_WALLET_REPO.local_repo_path() as repo_dir:
        root_data_dir = path.join(repo_dir, 'dist', 'tokens')
        tokens: List[Token] = []

        for subdir, blockchain in DIRS_TO_IMPORT.items():
            token_data_file = path.join(root_data_dir, subdir, f"tokens-{subdir}.json")
            print_dim(f"Processing '{blockchain}' file: '{token_data_file}'...")

            with open(token_data_file, 'r') as json_file:
                tokens_info = json.load(json_file)

            for token_info in tokens_info:
                token = Token(
                    blockchain=blockchain,
                    token_type=token_info.get('type'),  # Not always provided
                    address=token_info[ADDRESS],
                    symbol=token_info[SYMBOL],
                    name=token_info[NAME],
                    decimals=token_info['decimals'],
                    data_source=MY_ETHER_WALLET_REPO.repo_url
                )

                tokens.append(token)

        insert_tokens_from_data_source(tokens)
