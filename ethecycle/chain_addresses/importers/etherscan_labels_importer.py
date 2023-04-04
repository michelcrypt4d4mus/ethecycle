import json
from collections import defaultdict
from os import path
from typing import List

from rich.panel import Panel
from rich.pretty import pprint

from ethecycle.blockchains.arbitrum import Arbitrum
from ethecycle.blockchains.avalanche import Avalanche_C_Chain
from ethecycle.blockchains.binance_smart_chain import BinanceSmartChain
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.blockchains.fantom import Fantom
from ethecycle.blockchains.optimism import Optimism
from ethecycle.blockchains.polygon import Polygon
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.chain_addresses.config.etherscan import determine_category
from ethecycle.chain_addresses.github_data_source import GithubDataSource
from ethecycle.config import Config
from ethecycle.models.wallet import Wallet
from ethecycle.util.dict_helper import sort_dict
from ethecycle.util.filesystem_helper import subdirs_of_dir
from ethecycle.util.logging import console, log, print_address_import
from ethecycle.util.string_constants import *

SOURCE_REPO = GithubDataSource('brianleect/etherscan-labels')

SUBDIR_TO_BLOCKCHAIN_MAPPING = {
    'arbiscan': Arbitrum,
    AVALANCHE: Avalanche_C_Chain,
    'bscscan': BinanceSmartChain,
    'etherscan': Ethereum,
    'ftmscan': Fantom,
    'optimism': Optimism,
    'polygonscan': Polygon,
}


def import_etherscan_labels_repo():
    """Import data from ethereum-lists tokens repo. Has chains besides ethereum."""
    print_address_import(SOURCE_REPO.repo_url)

    with SOURCE_REPO.local_repo_path() as repo_dir:
        data_dir = path.join(repo_dir, 'data')
        wallets: List[Wallet] = []

        for subdir in subdirs_of_dir(data_dir):
            blockchain = SUBDIR_TO_BLOCKCHAIN_MAPPING[path.basename(subdir)]
            addresses_file = path.join(subdir, 'combined', 'combinedAllLabels.json')
            label_counts = defaultdict(lambda: 0)
            uncategorized_label_counts = defaultdict(lambda: 0)
            log.info(f"Processing {addresses_file}...")

            with open(addresses_file, newline='') as json_file:
                for address, data in json.load(json_file).items():
                    if len(address) == 0:
                        log.warning("Skipping empty address with labels {data['labels']}")
                        continue

                    log.debug(f"Address: {address}\ndata:\n{data}\n\n")
                    labels = data['labels']
                    labels_str = ', '.join(sorted(labels))
                    label_counts[labels_str] += 1
                    category = determine_category(labels)

                    if category is None:
                        #console.print(f"{address}: {data['name']}\n    {labels}\n")
                        uncategorized_label_counts[labels_str] += 1

                    wallet = Wallet(
                        address=address,
                        chain_info=blockchain,
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
