import pytest

from ethecycle.models.transaction import Txn
from ethecycle.util.string_constants import *

from tests.ethecycle.models.conftest import EXTRACTION_TIMESTAMP_STR, TEST_TXN_HASH, TEST_TXN_LOG_LEVEL


def test_constructor(transaction_of_the_beast):
    assert transaction_of_the_beast.transaction_id == f"{TEST_TXN_HASH}-{TEST_TXN_LOG_LEVEL}"
    assert transaction_of_the_beast.num_tokens == 6
    assert transaction_of_the_beast.symbol == 'S1X'


def test_to_neo4j_csv_row(token_of_the_beast, transaction_of_the_beast, wallet_1, wallet_2):
    assert transaction_of_the_beast.to_neo4j_csv_row() == [
        transaction_of_the_beast.transaction_id,
        transaction_of_the_beast.blockchain,
        token_of_the_beast.address,
        token_of_the_beast.symbol,
        wallet_1.address,
        wallet_2.address,
        6,
        666666,
        EXTRACTION_TIMESTAMP_STR
    ]
