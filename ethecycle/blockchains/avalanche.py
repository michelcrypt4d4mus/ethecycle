# AVAX has multiple chains, format info here:
# Avalanche (AVAX) – AVAX addresses use a Bech32 addressing format. Avalanche is not prescriptive about addressing schemes. Each Virtual Machine (VM) may select its own addressing scheme. The Avalanche C-Chain, which follows the Ethereum VM addressing system, has addresses that begin with “C”. The Avalanche X-Chain and P-Chain use a binary 20-byte array for raw addresses, begin with “X” and “P” respectively. Every address, regardless of its first character, is followed by “avax1” to make it clear users are sending funds on the Avalanche blockchain network.
import re
from ethecycle.blockchains.chain_info import ChainInfo


class Avalanche_P_Chain(ChainInfo):
    ADDRESS_PREFIXES = ['P-avax']

    @classmethod
    def chain_string(cls) -> str:
        return 'avax-p'


class Avalanche_C_Chain(ChainInfo):
    ADDRESS_PREFIXES = ['0x']  # Also just '0x'

    @classmethod
    def chain_string(cls) -> str:
        return 'avax-c'


class Avalanche_X_Chain(ChainInfo):
    ADDRESS_PREFIXES = ['X-avax']

    @classmethod
    def chain_string(cls) -> str:
        return 'avax-x'
