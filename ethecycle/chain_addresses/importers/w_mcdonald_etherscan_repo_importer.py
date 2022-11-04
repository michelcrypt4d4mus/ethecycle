import csv
from os import path
from typing import List

from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.chain_addresses.address_db import insert_wallets_from_data_source
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.util.logging import print_address_import
from ethecycle.util.string_constants import *
from ethecycle.wallet import Wallet

SOURCE_REPO = GithubDataSource('W-McDonald/etherscan')


def import_w_mcdonald_etherscan_addresses():
    """Import data from ethereum-lists tokens repo."""
    print_address_import(SOURCE_REPO.repo_url)

    with SOURCE_REPO.local_repo_path() as repo_dir:
        addresses_file = path.join(repo_dir, 'addresses.csv')
        wallets: List[Wallet] = []

        with open(addresses_file, newline='') as csvfile:
            for row in csv.DictReader(csvfile, delimiter=','):
                address = row[ADDRESS]
                category = row['label']

                if not Ethereum.is_valid_address(address):
                    if address.startswith('x'):
                        address = '0' + address
                    else:
                        raise ValueError('Not a valid address: ' + address)

                if category == 'Exchange':
                    category = 'cex'
                elif category == 'Lending':
                    category = 'cefi'

                wallet = Wallet(
                    address=address,
                    chain_info=Ethereum,
                    label=row['entity'],
                    category=category,
                    data_source=SOURCE_REPO.repo_url
                )

                wallets.append(wallet)

        insert_wallets_from_data_source(wallets)
