# Simple class to hold wallet info
# TODO: maybe compute the date or block_number of first txion? Maybe better done in-graph...
from dataclasses import dataclass
from typing import List

from ethecycle.blockchains import get_chain_info
from ethecycle.transaction import Txn

MISSING_ADDRESS = 'no_address'


@dataclass
class Wallet:
    address: str
    blockchain: str

    def __post_init__(self):
        # Some txns have multiple internal transfers so append log_index to achieve uniqueness
        chain_info = get_chain_info(self.blockchain)
        self.label = chain_info.wallet_label(self.address)
        self.category = chain_info.wallet_category(self.address)

    @classmethod
    def extract_wallets_from_transactions(cls, txns: List[Txn]) -> List['Wallet']:
        """Extract wallet address from from/to addresses and add labels. Assumes all txns have same chain."""
        blockchains = list(set([t.blockchain for t in txns]))

        if len(blockchains) != 1:
            raise ValueError(f"Multiple blockchains found in this set of txns: {blockchains}")

        wallet_addresses = set([txn.to_address for txn in txns]).union(set([txn.from_address for txn in txns]))
        wallet_addresses.remove('')
        wallet_addresses.add(MISSING_ADDRESS)
        return [Wallet(address, blockchains[0]) for address in wallet_addresses]
