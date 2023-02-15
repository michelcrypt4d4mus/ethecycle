import csv
import gzip
from os import path
from typing import List

from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.models.wallet import Wallet
from ethecycle.util.filesystem_helper import RAW_DATA_DIR
from ethecycle.util.string_constants import DATA_SOURCE

OKX_ADDRESS_CSV = str(RAW_DATA_DIR.joinpath('okx_proof_of_reserves_addresses.csv.gz'))
OKX_DATA_SOURCE = path.basename(OKX_ADDRESS_CSV)


def import_okx_addresses():
    with gzip.open(OKX_ADDRESS_CSV, mode='rt') as csvfile:
        wallets: List[Wallet] = []

        for row in csv.DictReader(csvfile, delimiter=','):
            row[DATA_SOURCE] = OKX_DATA_SOURCE
            del row['comment']
            wallets.append(Wallet(**row))

    insert_addresses(wallets)
