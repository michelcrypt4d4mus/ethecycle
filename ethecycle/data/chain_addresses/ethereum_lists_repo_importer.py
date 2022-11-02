"""
Import data from ethereum-lists repo.
# TODO: They also have a contracts repo we could import: https://github.com/ethereum-lists/contracts
"""
import json
from os import path
from typing import List

from ethecycle.blockchains.token import Token
from ethecycle.config import Config
from ethecycle.data.chain_addresses.address_db import delete_rows_from_source, insert_tokens
from ethecycle.data.chain_addresses.db import TOKENS_TABLE_NAME
from ethecycle.data.chain_addresses.github_data_source import GithubDataSource
from ethecycle.util.filesystem_helper import files_in_dir
from ethecycle.util.logging import console, log
from ethecycle.util.string_constants import *

SOURCE_REPO = GithubDataSource('https://github.com/ethereum-lists/tokens.git')

# Keys are folder names, values are blockchain names.
DIRS_TO_IMPORT = {
    'arb': 'Abitrum',
    'avax': 'Avalanche',
    'bsc': 'Binance Smart Chain',
    'eth': ETHEREUM,
}


def import_ethereum_lists_addresses():
    """Import data from ethereum-lists data repo."""
    console.print("Importing ethereum-lists repo chain addresses...")
    root_data_dir = path.join(SOURCE_REPO.local_repo_path(), 'tokens')
    tokens: List[Token] = []

    for subdir, blockchain in DIRS_TO_IMPORT.items():
        log.info(f"    Processing {blockchain}...")
        token_data_dir = path.join(root_data_dir, subdir)

        for token_info_json_file in files_in_dir(token_data_dir):
            try:
                with open(token_info_json_file, 'r') as json_file:
                    token_info = json.load(json_file)

                token = Token(
                    blockchain=blockchain,
                    token_type=token_info.get('type'),  # Not always provided
                    address=token_info['address'],
                    symbol=token_info['symbol'],
                    name=token_info['name'],
                    decimals=token_info['decimals'],
                    data_source=SOURCE_REPO.repo_url
                )

                tokens.append(token)
            except KeyError as e:
                log.warning(f"Error parsing '{token_info_json_file}': {e}")

    delete_rows_from_source(TOKENS_TABLE_NAME, SOURCE_REPO.repo_url)
    insert_tokens(tokens)
