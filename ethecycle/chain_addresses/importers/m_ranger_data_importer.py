# Import address data from M. Ranger.
# Columns: address,owner,source,confidence,note,note 2,


import csv
import gzip
from os import path
from pathlib import Path
from typing import List

from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.models.wallet import Wallet
from ethecycle.util.logging import log
from ethecycle.util.filesystem_helper import RAW_DATA_DIR, files_in_dir
from ethecycle.util.string_constants import ADDRESS, DATA_SOURCE

M_RANGER_ADDRESSES_DIR = str(RAW_DATA_DIR.joinpath('m_ranger_wallet_addresses'))
M_RANGER_DATA_SOURCE = 'M. Ranger'

def import_m_ranger_wallet_tags():
    wallets: List[Wallet] = []

    for file in files_in_dir(M_RANGER_ADDRESSES_DIR):
        blockchain = Path(file).with_suffix('').with_suffix('').name
        log.info(f"Processing M.Ranger file for {blockchain} '{file}'...")

        with gzip.open(file, mode='rt') as csvfile:
            for row in csv.DictReader(csvfile, delimiter=','):
                log.debug(row)
                confidence = row['confidence']
                source = row['source']

                if source is not None and len(source.strip()) > 0:
                    comment = 'source: '
                else:
                    comment = ''

                comment += ' '.join([source, row['note'], row['note 2']]).strip()

                if confidence is not None and len(confidence) > 0:
                    comment += f" ({confidence}% confidence)"

                wallet = Wallet(
                    address=row[ADDRESS],
                    blockchain=blockchain,
                    name=row['owner'],
                    comment=comment,
                    data_source=M_RANGER_DATA_SOURCE
                )

                log.debug(wallet)
                wallets.append(wallet)
                # row[DATA_SOURCE] = OKX_DATA_SOURCE
                # del row['comment']
                # wallets.append(Wallet(**row))

    insert_addresses(wallets)
