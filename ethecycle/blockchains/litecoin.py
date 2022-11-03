from ethecycle.blockchains.chain_info import ChainInfo


class Litecoin(ChainInfo):
    SHORT_NAME = 'ltc'
    ADDRESS_PREFIXES = ['L', 'M', 'ltc1']  # Also '3'...
