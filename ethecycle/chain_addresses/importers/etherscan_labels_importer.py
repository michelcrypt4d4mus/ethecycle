import json
from collections import defaultdict
from os import path
from typing import List

from rich.panel import Panel
from rich.pretty import pprint

from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.chain_addresses.config.etherscan import determine_category
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.config import Config
from ethecycle.util.dict_helper import sort_dict
from ethecycle.util.logging import console, print_address_import
from ethecycle.util.string_constants import *
from ethecycle.models.wallet import Wallet

SOURCE_REPO = GithubDataSource('brianleect/etherscan-labels')


def import_etherscan_labels_repo():
    """Import data from ethereum-lists tokens repo."""
    print_address_import(SOURCE_REPO.repo_url)

    with SOURCE_REPO.local_repo_path() as repo_dir:
        addresses_file = path.join(repo_dir, 'combined', 'combinedLabels.json')
        wallets: List[Wallet] = []
        label_counts = defaultdict(lambda: 0)
        uncategorized_label_counts = defaultdict(lambda: 0)

        with open(addresses_file, newline='') as json_file:
            for address, data in json.load(json_file).items():
                labels = data['labels']
                labels_str = ', '.join(sorted(labels))
                label_counts[labels_str] += 1
                category = determine_category(labels)

                if category is None:
                    #console.print(f"{address}: {data['name']}\n    {labels}\n")
                    uncategorized_label_counts[labels_str] += 1

                wallet = Wallet(
                    address=address,
                    chain_info=Ethereum,
                    name=data[NAME],
                    category=category,
                    data_source=SOURCE_REPO.repo_url
                )

                wallets.append(wallet)

        if Config.debug:
            console.print(Panel('UNCATEGORIZED'))
            pprint(sort_dict(uncategorized_label_counts))
            console.print(Panel('CATEGORIZED'))
            pprint(sort_dict(label_counts))

        insert_addresses(wallets)
