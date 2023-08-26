"""
FTX top couple hundred wallets by volume.
"""
from ethecycle.chain_addresses.importers.dune_copy_paste_file_reader import DuneCopyPasteReader
from ethecycle.util.filesystem_helper import RAW_DATA_DIR
from ethecycle.util.string_constants import ETHEREUM, ETHEREUM

DATA_SOURCE = 'https://dn.com/queries/1543801/2586852'
DUNE_FILE = str(RAW_DATA_DIR.joinpath('ftx_major_partners.txt'))


def import_ftx_biggest_trading_partners():
    DuneCopyPasteReader(DUNE_FILE, ETHEREUM, 'FTX/Alameda', DATA_SOURCE).extract_wallets()
