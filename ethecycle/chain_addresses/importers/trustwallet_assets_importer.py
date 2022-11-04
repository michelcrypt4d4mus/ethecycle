"""
Trustwallet's actively maintained repo.
Details: https://developer.trustwallet.com/assets/repository_details
"""

import json
from collections import defaultdict
from os import path
from pathlib import Path
from typing import List

from rich.panel import Panel

from ethecycle.blockchains.blockchains import CHAIN_IDS, get_chain_info
from ethecycle.models.token import Token
from ethecycle.chain_addresses.address_db import (insert_tokens_from_data_source,
     insert_wallets_from_data_source)
from ethecycle.chain_addresses.db.table_definitions import TOKENS_TABLE_NAME, WALLETS_TABLE_NAME
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.config import Config
from ethecycle.util.filesystem_helper import files_in_dir, subdirs_of_dir
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *
from ethecycle.models.wallet import Wallet

SOURCE_REPO = GithubDataSource('trustwallet/assets', 'trustwallet_assets')

# Folders that are the same name as the chain
DIRS_TO_IMPORT = [
    BITCOIN,
    CARDANO,
    ETHEREUM,
    SOLANA,
]

MAPPED_DIRS_TO_IMPORT = {chain: chain for chain in DIRS_TO_IMPORT}

# Folders that need to be mapped
MAPPED_DIRS_TO_IMPORT.update({
    BINANCE: BINANCE_SMART_CHAIN,
    'bitcoincash': BITCOIN_CASH,
})


def import_trust_wallet_repo():
    """Import data from trust wallet assets repo."""
    print_address_import(SOURCE_REPO.repo_url)

    with SOURCE_REPO.local_repo_path() as repo_dir:
        root_data_dir = path.join(repo_dir, 'blockchains')
        tokens: List[Token] = []
        wallets: List[Wallet] = []

        for subdir, blockchain in MAPPED_DIRS_TO_IMPORT.items():
            console.print(f"Processing {blockchain}...")
            chain_data_dir = path.join(root_data_dir, subdir)
            tokens_dir = path.join(chain_data_dir, 'assets')
            validators_dir = path.join(chain_data_dir, 'validators')
            # TODO: this file has something about trading pairs something something?
            token_list_json = path.join(chain_data_dir, 'tokenlist.json')

            if path.exists(tokens_dir):
                chain_tokens = _get_tokens_for_chain(blockchain, tokens_dir)
                tokens.extend(chain_tokens)
            else:
                log.info(f"    No token assets dir in '{subdir}'...")

            if path.exists(validators_dir):
                validator_wallets = _get_validator_wallets_for_chain(blockchain, validators_dir)
                wallets.extend(validator_wallets)
            else:
                log.info(f"    No validators assets dir in '{subdir}'...")

        insert_tokens_from_data_source(tokens)
        insert_wallets_from_data_source(wallets)


def _get_tokens_for_chain(blockchain: str, tokens_dir: str) -> List[Token]:
    tokens: List[Token] = []

    for subdir in subdirs_of_dir(tokens_dir):
        token_info_json_file = path.join(subdir, 'info.json')

        try:
            with open(token_info_json_file, 'r') as json_file:
                token_info = json.load(json_file)

            token_status = token_info['status']

            # Unclear if status of 'spam' means active or inactive
            if token_status == 'spam':
                is_active = None
                is_scam = True
            else:
                is_active = token_status == 'active'
                is_scam = None

            token = Token(
                blockchain=blockchain,
                token_type=token_info.get('type'),  # Not always provided
                address=token_info['id'],
                symbol=token_info[SYMBOL],
                name=token_info[NAME],
                decimals=token_info['decimals'],
                is_active=is_active,
                is_scam=is_scam,
                url_explorer=token_info.get('explorer'),
                data_source=SOURCE_REPO.repo_url
            )

            if Config.debug:
                console.print(Panel(f"{token_info['id']} ({path.basename(subdir)})", expand=False))
                print(token_info)
                print("\n\n---------------------\n\n")
                print(token)

            tokens.append(token)
        except KeyError as e:
            log.warning(f"Error parsing '{token_info_json_file}': {e}")

    console.print(f"  Found {len(tokens)} tokens for {blockchain}...", style='dim')
    return tokens


def _get_validator_wallets_for_chain(blockchain: str, validators_dir: str) -> List[Wallet]:
    wallets: List[Wallet] = []
    validator_json = path.join(validators_dir, 'list.json')

    try:
        with open(validator_json, 'r') as json_file:
            validators_info = json.load(json_file)

        for validator in validators_info:
            wallet = Wallet(
                address=validator['id'],
                chain_info=get_chain_info(blockchain),
                label=validator[NAME],
                category='validator',
                data_source=SOURCE_REPO.repo_url
            )

            if Config.debug:
                console.print(Panel(f"{validator['id']} ({path.basename(validators_dir)})", expand=False))
                print(validator)

            wallets.append(wallet)
    except KeyError as e:
        log.warning(f"Error parsing '{validator_json}': {e}")

    console.print(f"  Found {len(wallets)} validators for {blockchain}...", style='dim')
    return wallets
