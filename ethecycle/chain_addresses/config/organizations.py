"""
Offers methods that map from a wallet name/category to organizations, e.g. groups
Alameda and FTX into one org 'Alameda/FTX'.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from ethecycle.util.string_constants import *

CASE_SENSITIVE = 'case_sensitive'

@dataclass
class NameToOrg:
    substring: str
    organization: str
    case_sensitive: bool = False
    excluded: List[str] = field(default_factory=list)

    def is_match(self, name: str) -> bool:
        if name in self.excluded:
            return False

        if self.case_sensitive:
            return self.substring in name
        else:
            return self.substring.lower() in name.lower()

    @classmethod
    def get_org_for_name(cls, name: str) -> Optional[str]:
        return next((matcher.organization for matcher in SUBSTRINGS_TO_ORGS if matcher.is_match(name)), None)

# If the key is a substring of the wallet name the org will be the value.
SUBSTRINGS_TO_ORGS = [
    NameToOrg(AAVE, AAVE),
    NameToOrg(BINANCE, BINANCE),
    NameToOrg(
        FTX,
        'Alameda/FTX',
        case_sensitive=True,
        excluded=['@DakotaLameda', '@TanjaLameda', 'BoycottFTX', 'Binance Wallet for FTX Token ($FTT)', '@ftxjqbhmgv5707']
    )
]
