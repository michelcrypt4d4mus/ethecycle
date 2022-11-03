"""
Import data from ethereum-lists repo.
# TODO: They also have a contracts repo we could import: https://github.com/ethereum-lists/contracts
"""
import json
from os import path
from pathlib import Path
from typing import List

from ethecycle.blockchains.blockchains import CHAIN_IDS, get_chain_info
from ethecycle.blockchains.token import Token
from ethecycle.chain_addresses.address_db import (delete_rows_from_source, insert_tokens,
     insert_wallets)
from ethecycle.chain_addresses.db.table_definitions import TOKENS_TABLE_NAME, WALLETS_TABLE_NAME
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.util.filesystem_helper import files_in_dir, subdirs_of_dir
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *
from ethecycle.wallet import Wallet

TOKENS_REPO = GithubDataSource('ethereum-lists/tokens')
CONTRACTS_REPO = GithubDataSource('ethereum-lists/contracts')
CONTRACT_JSON_KEYS = set(['project', NAME, 'source', 'features'])

# Keys are folder names, values are blockchain names.
DIRS_TO_IMPORT = {
    'arb': 'Abitrum',
    'avax': 'Avalanche',
    'bsc': 'Binance Smart Chain',
    'eth': ETHEREUM,
}


def import_ethereum_lists_addresses():
    _import_ethereum_lists_tokens_addresses()
    _import_contract_addresses()


def _import_ethereum_lists_tokens_addresses():
    """Import data from ethereum-lists tokens repo."""
    print_address_import(TOKENS_REPO.repo_url)
    root_data_dir = path.join(TOKENS_REPO.local_repo_path(), 'tokens')
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
                    address=token_info[ADDRESS],
                    symbol=token_info[SYMBOL],
                    name=token_info[NAME],
                    decimals=token_info['decimals'],
                    data_source=TOKENS_REPO.repo_url
                )

                tokens.append(token)
            except KeyError as e:
                log.warning(f"Error parsing '{token_info_json_file}': {e}")

    delete_rows_from_source(TOKENS_TABLE_NAME, TOKENS_REPO.repo_url)
    insert_tokens(tokens)


def _import_contract_addresses():
    """Import data from ethereum-lists contracts data repo."""
    print_address_import(CONTRACTS_REPO.repo_url)
    root_data_dir = path.join(CONTRACTS_REPO.local_repo_path(), 'contracts')
    contracts: List[Wallet] = []

    for chain_id_dir in subdirs_of_dir(root_data_dir):
        dir_basename = Path(chain_id_dir).stem
        blockchain = CHAIN_IDS.get(int(dir_basename))

        if blockchain is None:
            log.warning(f"Unknown chain ID {dir_basename}; will not process '{chain_id_dir}'")
            continue

        log.info(f"  Loading contracts for '{blockchain}' from '{chain_id_dir}'...")

        for contract_json_file in files_in_dir(chain_id_dir):
            contract_file_basename = path.basename(contract_json_file)
            log.debug(f"    Processing {contract_file_basename}")

            try:
                with open(contract_json_file, 'r') as json_file:
                    contract_info = json.load(json_file)
                    log.debug(f"    JSON: {contract_info}")
                    keys = set(contract_info.keys())

                if not keys.issubset(CONTRACT_JSON_KEYS):
                    other_keys = keys.difference(CONTRACT_JSON_KEYS)
                    console.print(f"{contract_file_basename} nonstandard keys: {list(other_keys)}", style='bright_yellow')

                contract = Wallet(
                    address=Path(contract_json_file).stem,
                    chain_info=get_chain_info(blockchain),
                    label=f"{contract_info.get('project')}: {contract_info.get(NAME)}",
                    category=CONTRACT,
                    data_source=CONTRACTS_REPO.repo_url
                )

                contracts.append(contract)
            except KeyError as e:
                log.warning(f"Error parsing '{contract_json_file}': {e}")

    delete_rows_from_source(WALLETS_TABLE_NAME, CONTRACTS_REPO.repo_url)
    insert_wallets(contracts)
