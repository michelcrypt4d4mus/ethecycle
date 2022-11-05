import csv
from os import path
from typing import List

from ethecycle.blockchains.blockchains import get_chain_info
from ethecycle.chain_addresses.address_db import insert_wallets_from_data_source
from ethecycle.models.wallet import Wallet
from ethecycle.util.filesystem_helper import RAW_DATA_DIR
from ethecycle.util.string_constants import BLOCKCHAIN, DATA_SOURCE

HAND_COLLATED_ADDRESS_CSV = str(RAW_DATA_DIR.joinpath('hand_collated.csv'))
HAND_COLLATED_DATA_SOURCE = path.basename(HAND_COLLATED_ADDRESS_CSV)


def import_hand_collated_addresses():
    with open(HAND_COLLATED_ADDRESS_CSV, newline='') as csvfile:
        wallets: List[Wallet] = []

        for row in csv.DictReader(csvfile, delimiter=','):
            row['chain_info'] = get_chain_info(row[BLOCKCHAIN])
            del row[BLOCKCHAIN]
            row[DATA_SOURCE] = HAND_COLLATED_DATA_SOURCE
            wallets.append(Wallet(**row))

    insert_wallets_from_data_source(wallets)
