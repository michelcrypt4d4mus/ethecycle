"""
Import jconorgrogan's compiled list of wallets whose tokens are lost forever because of
typos or bugs or anything else.
"""
import csv
from os import path
from typing import List

from rich.panel import Panel

from ethecycle.blockchains.blockchains import CHAIN_IDS
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.models.blockchain import guess_chain_info_from_address
from ethecycle.models.token import Token
from ethecycle.models.wallet import Wallet
from ethecycle.util.dict_helper import walk_json
from ethecycle.util.filesystem_helper import files_in_dir, get_lines, load_file_contents, subdirs_of_dir
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *

LOST_ETH_REPO = GithubDataSource('jconorgrogan/Lost-ETH')
LOST_BTC_REPO = GithubDataSource('jconorgrogan/BTC-Burn-Addresses')
BTC_ADDRESS_LINE_PREFIX = '- '


def import_lost_forever_addresses():
    wallets: List[Wallet] = []

    with LOST_BTC_REPO.local_repo_path() as repo_dir:
        for line in get_lines(path.join(repo_dir, 'README.md')):
            if not line.startswith(BTC_ADDRESS_LINE_PREFIX):
                log.info(f"Skipping line: '{line}'")
                continue

            wallet = Wallet(
                blockchain='bitcoin',
                address=line.removeprefix(BTC_ADDRESS_LINE_PREFIX).strip(),
                name='Lost forever because there is no private key owner',
                category='lost',
                data_source=LOST_BTC_REPO.repo_url
            )

            wallets.append(wallet)
            log.debug(wallet)

    insert_addresses(wallets)
    wallets = []

    with LOST_ETH_REPO.local_repo_path() as repo_dir:
        with open(path.join(repo_dir, 'Lost Eth.csv'), newline='') as csvfile:
            for row in csv.DictReader(csvfile, delimiter=","):
                if row['Address'] == '0x0000000000000000000000000000000000000000':
                    continue

                if row['Type'].startswith('Parity'):
                    organization = 'Parity'
                    comment = 'Funds lost forever: https://techcrunch.com/2017/12/05/parity-ceo-says-shes-confident-that-its-280m-in-frozen-ethereum-isnt-lost-forever/'

                    if row['Comment'] == '':
                        name = row['Type']
                    else:
                        name = f"{row['Comment']} {row['Type']}"
                else:
                    name=f"Funds lost forever due to {row['Type']}"
                    organization = None
                    row_comment = row['Comment']

                    if 'Pfeffer' in row_comment:
                        comment = 'From query by Johannes Pfeffer'
                    elif row_comment == '':
                        comment = None
                    else:
                        comment = row_comment

                wallet = Wallet(
                    address=row['Address'],
                    blockchain='ethereum',
                    name=name,
                    category='lost',
                    comment=comment,
                    organization=organization,
                    data_source = LOST_ETH_REPO.repo_url
                )

                log.debug(wallet)
                wallets.append(wallet)

    insert_addresses(wallets)
