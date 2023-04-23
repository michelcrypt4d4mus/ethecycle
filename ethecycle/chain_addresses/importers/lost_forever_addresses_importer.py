"""
Import jconorgrogan's compiled list of wallets whose tokens are lost forever because of
typos or bugs or anything else.
"""
import csv
from os import path
from typing import List


from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.models.wallet import Wallet
from ethecycle.util.filesystem_helper import get_lines
from ethecycle.util.logging import log
from ethecycle.util.string_constants import *

LOST_ETH_REPO = GithubDataSource('jconorgrogan/Lost-ETH')
LOST_BTC_REPO = GithubDataSource('jconorgrogan/BTC-Burn-Addresses')
BTC_ADDRESS_LINE_PREFIX = '- '
LOST = 'lost'


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
                category=LOST,
                data_source=LOST_BTC_REPO.repo_url
            )

            wallets.append(wallet)
            log.debug(wallet)

    insert_addresses(wallets)
    wallets = []

    with LOST_ETH_REPO.local_repo_path() as repo_dir:
        with open(path.join(repo_dir, 'Lost Eth.csv'), newline='') as csvfile:
            for row in csv.DictReader(csvfile, delimiter=","):
                address = row['Address']
                row_comment = row['Comment']

                if address == '0x0000000000000000000000000000000000000000':
                    continue

                organization = None
                category = None
                comment = None

                if row['Type'].startswith('Parity'):
                    comment = 'Funds lost to Parity wallet disaster'
                    category = WALLET

                    if row_comment == '':
                        name = row['Type'] + ' (lost forever)'
                        organization = 'Parity'
                    else:
                        name = f"{row_comment} {row['Type']} ({LOST} forever)"
                        organization = row_comment
                elif address.startswith('0x00000000000000000000000000000000000'):
                    name = 'Burn address'
                    category = 'burn'
                else:
                    name=f"Funds lost forever due to {row['Type']}"
                    row_comment = row_comment

                    if 'Pfeffer' in row_comment:
                        comment = 'From query by Johannes Pfeffer'
                    elif row_comment == '':
                        comment = None
                    else:
                        comment = row_comment

                wallet = Wallet(
                    address=address,
                    blockchain=ETHEREUM,
                    name=name,
                    category=category or LOST,
                    comment=comment,
                    organization=organization,
                    data_source = LOST_ETH_REPO.repo_url
                )

                log.debug(wallet)
                wallets.append(wallet)

    insert_addresses(wallets)
