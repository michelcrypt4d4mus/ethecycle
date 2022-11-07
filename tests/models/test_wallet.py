from ethecycle.models.wallet import Wallet
from ethecycle.util.string_constants import *

from tests.models.conftest import EXTRACTION_TIMESTAMP_STR


def test_to_neo4j_csv_row(wallet_1):
    assert wallet_1.to_neo4j_csv_row() == [
        wallet_1.address,
        ETHEREUM,
        'Gabriel',
        CEX,
        EXTRACTION_TIMESTAMP_STR
    ]


def test_from_token(token_of_the_beast):
    token_wallet = Wallet.from_token(token_of_the_beast)
    assert token_wallet.address == token_of_the_beast.address
    assert token_wallet.name == token_of_the_beast.symbol + ' Token'
    assert token_wallet.category == TOKEN
    assert token_wallet.extracted_at == token_of_the_beast.extracted_at


def test_token_name_at_wallet_address(prep_db):
    name = Wallet.name_at_address(ETHEREUM, USDT_ETHEREUM_ADDRESS).lower()
    assert 'tether' in name or 'usdt' in name
