from datetime import datetime

import pytest
from rich.pretty import pprint

from ethecycle.models.token import Token
from ethecycle.models.transaction import Txn
from ethecycle.util.logging import console
from ethecycle.util.string_constants import *

from tests.ethecycle.models.conftest import EXTRACTION_TIMESTAMP_STR, TEST_TXN_HASH, TEST_TXN_LOG_LEVEL

TOKEN_LAUNCHED_AT = datetime(2019, 10, 5, 18, 00)
URL_PROPERTIES = 'discord telegram chat announcement explorer message_board reddit source_code'.split()


def test_from_properties(token_of_the_beast):
    properties = token_of_the_beast.__dict__

    properties.update({
        'is_active': True,
        'is_scam': True,
        'is_hidden': True,
        'is_audited': True,
        'had_an_ico': True,
        'launched_at': TOKEN_LAUNCHED_AT,
        'listed_on_coin_market_cap_at': TOKEN_LAUNCHED_AT,
        'coin_market_cap_watchers': 6666,
        'coin_market_cap_id': 666
    })

    for url_property in URL_PROPERTIES:
        properties[f"url_{url_property}"] = f"http://{url_property}.com"

    token = Token.from_properties(properties)
    assert token.launched_at == TOKEN_LAUNCHED_AT
    assert token.listed_on_coin_market_cap_at == TOKEN_LAUNCHED_AT

    assert token.extra_fields == {
        'is_hidden': True,
        'is_audited': True,
        'had_an_ico': True,
        'coin_market_cap_watchers': 6666,
        'coin_market_cap_id': 666,
        'url_discord': 'http://discord.com',
        'url_telegram': 'http://telegram.com',
        'url_chat': 'http://chat.com',
        'url_announcement': 'http://announcement.com',
        'url_message_board': 'http://message_board.com',
        'url_reddit': 'http://reddit.com',
        'url_source_code': 'http://source_code.com',
    }
