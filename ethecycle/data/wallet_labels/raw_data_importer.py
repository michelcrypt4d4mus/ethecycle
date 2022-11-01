"""
Import the data files in the raw_data/ dir
"""

import gzip
import json
from os import listdir, path
from typing import Dict, Optional

from ethecycle.blockchains.token import Token
from ethecycle.wallet import Wallet
from ethecycle.util.filesystem_helper import WALLET_LABELS_DIR
from ethecycle.util.logging import log
from ethecycle.util.string_constants import TOKEN

ADDRESS_PREFIX = '0x'
WALLET_FILE_EXTENSION = '.txt.gz'
ETHERSCRAP_FILE = RAW_DATA_DIR.joinpath('etherscrape.txt.gz')


def import_ethereum_from_dune() -> None:
